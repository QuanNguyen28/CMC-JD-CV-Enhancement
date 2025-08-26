# src/services/retriever_service.py
from typing import List, Optional
from pydantic import BaseModel
from pymilvus import connections, Collection
from src.schemas.retriever import RetrieveSimilarReq, RetrieveReq, ChunkResult
from src.core.config import MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION
import os

# ---- Milvus init ----
connections.connect("default", host=MILVUS_HOST, port=str(MILVUS_PORT))
collection = Collection(MILVUS_COLLECTION)
collection.load()

def _resolve_path_field(col: Collection) -> Optional[str]:
    """Tự dò tên cột lưu đường dẫn file trong schema Milvus."""
    names = {f.name for f in col.schema.fields}
    for cand in ("object_path", "object_url", "file_path", "path"):
        if cand in names:
            return cand
    return None

PATH_FIELD = _resolve_path_field(collection)
BASE_FIELDS = ["chunk_id", "jd_id", "chunk_index"]
OUTPUT_FIELDS = BASE_FIELDS + ([PATH_FIELD] if PATH_FIELD else [])

def _safe_get(hit, key: str):
    try:
        if hasattr(hit, "entity") and hit.entity is not None:
            return hit.entity.get(key)
        if hasattr(hit, "fields") and hit.fields is not None:
            return hit.fields.get(key)
    except Exception:
        pass
    return None

def _search_vectors(query_vec: List[float], top_k: int):
    # ưu tiên COSINE; nếu server không hỗ trợ thì dùng IP
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 50}}
    try:
        return collection.search(
            data=[query_vec],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=OUTPUT_FIELDS,
        )[0]
    except Exception:
        # fallback
        search_params = {"metric_type": "IP", "params": {"nprobe": 50}}
        return collection.search(
            data=[query_vec],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=OUTPUT_FIELDS,
        )[0]

def retrieve_similar(query_vec: List[float], top_k: int) -> List[ChunkResult]:
    hits = _search_vectors(query_vec, top_k)
    out: List[ChunkResult] = []
    for h in hits:
        out.append(ChunkResult(
            chunk_id   = _safe_get(h, "chunk_id"),
            jd_id      = int(_safe_get(h, "jd_id") or 0),
            chunk_index= int(_safe_get(h, "chunk_index") or 0),
            object_path= _safe_get(h, PATH_FIELD) if PATH_FIELD else None,
            score      = float(h.score),
            snippet    = None,  # chỉ metadata cho /similar
        ))
    return out

def _read_snippet_from_file(path: str, max_lines: int) -> Optional[str]:
    try:
        if not path or not os.path.exists(path):
            return None
        lines = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip("\n"))
        return "\n".join(lines) if lines else None
    except Exception:
        return None

def retrieve_with_snippet(query_vec: List[float], top_k: int, snippet_lines: int) -> List[ChunkResult]:
    hits = _search_vectors(query_vec, top_k)
    out: List[ChunkResult] = []
    for h in hits:
        obj_path = _safe_get(h, PATH_FIELD) if PATH_FIELD else None
        snippet = _read_snippet_from_file(obj_path, snippet_lines) if obj_path else None
        out.append(ChunkResult(
            chunk_id   = _safe_get(h, "chunk_id"),
            jd_id      = int(_safe_get(h, "jd_id") or 0),
            chunk_index= int(_safe_get(h, "chunk_index") or 0),
            object_path= obj_path,
            score      = float(h.score),
            snippet    = snippet,
        ))
    return out