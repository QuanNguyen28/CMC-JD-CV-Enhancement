# src/services/retriever_service.py
from __future__ import annotations

from typing import List, Dict, Optional
import re, math

from sqlalchemy.orm import Session
from pymilvus import connections, Collection

from src.core.config import MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION

# Embeddings: ưu tiên embed_texts([str]) -> List[List[float]]
try:
    from embeddings.utils.gemini_embed import embed_text as _embed_texts
except Exception:
    # fallback nếu bạn chỉ có embed_text(str) -> List[float]
    from src.embeddings.utils.gemini_embed import embed_texts as _embed_texts  # type: ignore

try:
    from integrations.minio_client import get_object_str  
except Exception:
    get_object_str = None  # optional


# ------------------ utils ------------------
_collection: Optional[Collection] = None

def _connect_col() -> Collection:
    """Connect Milvus và load collection 1 lần (singleton)."""
    global _collection
    if _collection is not None:
        return _collection
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    col = Collection(MILVUS_COLLECTION)
    try:
        col.load()
    except Exception:
        pass
    _collection = col
    return col

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _l2_norm(v):
    return math.sqrt(sum(float(x) * float(x) for x in v)) or 1.0

def _unit_normalize(vec):
    n = _l2_norm(vec)
    return [float(x) / n for x in vec]

def _to_similarity(distance: float) -> float:
    """
    Với COSINE, Milvus thường trả distance ≈ 1 - cosine_sim.
    Map về similarity để client “càng cao càng tốt”.
    """
    try:
        d = float(distance)
    except Exception:
        return 0.0
    if 0.0 <= d <= 1.0:
        return 1.0 - d
    return d

def _search_params(col: Collection) -> dict:
    """Chọn search params theo index hiện có, luôn dùng COSINE."""
    try:
        idx = (col.indexes or [None])[0]
        itype = (idx and (idx.params.get("index_type") or idx.params.get("IndexType"))) or ""
        itype = str(itype).upper()
        if "HNSW" in itype:
            return {"metric_type": "COSINE", "params": {"ef": 128}}
        if "IVF" in itype:
            return {"metric_type": "COSINE", "params": {"nprobe": 50}}
    except Exception:
        pass
    return {"metric_type": "COSINE", "params": {}}


# ------------------ public API ------------------
def semantic_retrieve(
    db: Session,               # giữ để sau này join thêm info từ DB nếu muốn
    query: str,
    top_k: int = 5,
    *,
    prefer_minio: bool = False,  # True: cố lấy snippet từ MinIO nếu có key/url
) -> List[Dict]:
    """
    Embed query (unit-norm) -> Milvus COSINE search -> trả [{jd_id, score, snippet?, chunk_id, chunk_index, object_url}]
    """
    q = _clean(query)
    if not q:
        return []

    # 1) Embedding
    qvecs = _embed_texts([q]) if callable(_embed_texts) else None
    if qvecs is None or not qvecs:
        raise RuntimeError("Embedding function not available")
    qvec = _unit_normalize(qvecs[0])

    # 2) Milvus search
    col = _connect_col()
    params = _search_params(col)
    res = col.search(
        data=[qvec],
        anns_field="embedding",  # phải trùng tên vector field trong collection của bạn
        param=params,
        limit=max(1, top_k),
        output_fields=["chunk_id", "jd_id", "chunk_index", "object_url"],
    )

    hits = res[0] if res else []
    out: List[Dict] = []
    for h in hits:
        # distance or score tuỳ phiên bản PyMilvus
        dist = getattr(h, "distance", None)
        if dist is None:
            dist = getattr(h, "score", 0.0)
        sim = _to_similarity(dist)

        e = getattr(h, "entity", None)
        if e is None:
            # một số bản có h.get(field) trực tiếp; nhưng để an toàn, yêu cầu entity
            raise RuntimeError("Milvus hit missing entity")

        chunk_id    = e.get("chunk_id")
        jd_id       = int(e.get("jd_id"))
        chunk_index = int(e.get("chunk_index"))
        object_url  = e.get("object_url") or ""

        # 3) Snippet: nếu bạn muốn xem nội dung chunk
        snippet = ""
        if prefer_minio and get_object_str:
            key_or_url = e.get("object_key") or object_url
            if key_or_url:
                try:
                    text = get_object_str(key_or_url)
                    snippet = (_clean(text))[:500]
                except Exception:
                    snippet = ""
        # nếu không prefer_minio, để UI tự fetch object_url khi cần

        out.append({
            "chunk_id":   chunk_id,
            "jd_id":      jd_id,
            "chunk_index": chunk_index,
            "object_url": object_url,
            "score":      float(sim),
            # "snippet":  snippet,  # bật nếu bạn muốn trả kèm nội dung
        })

    # sort lại theo similarity (phòng khi search đã trả đúng order rồi)
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:max(1, top_k)]