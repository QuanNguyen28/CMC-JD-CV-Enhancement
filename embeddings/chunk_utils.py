# src/embeddings/chunk_utils.py
from __future__ import annotations
from typing import List, Tuple

from src.core.config import MINIO_BUCKET
from embeddings.utils.gemini_embed import embed_text
from embeddings.utils.chunker import split_markdown

# optional MinIO save (nếu không dùng MinIO có thể để None)
try:
    from src.integrations.minio_client import put_object_str
except Exception:
    put_object_str = None  # type: ignore

def build_object_key(jd_id: int, chunk_index: int) -> str:
    # Dạng "bucket/key" để client dễ parse/presign: jdchunks/jd-123/chunk-0.md
    return f"{MINIO_BUCKET}/jd-{jd_id}/chunk-{chunk_index}.md"

def make_chunks(md: str) -> List[str]:
    return split_markdown(md or "")

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    # dùng embed_text (đã fix dim + unit-normalize)
    return embed_text(chunks)

def prepare_chunk_records(
    jd_id: int,
    md: str,
    *,
    save_to_minio: bool = True
) -> Tuple[List[str], List[int], List[int], List[str], List[List[float]]]:
    """
    Trả về dữ liệu sẵn sàng insert Milvus:
      - chunk_id (str): "jd{jd_id}_c{idx}"
      - jd_id (int)
      - chunk_index (int)
      - object_url (str): "bucket/key"
      - embedding (List[float])
    Đồng thời (tuỳ chọn) ghi raw chunk lên MinIO.
    """
    chunks = make_chunks(md)
    if not chunks:
        return [], [], [], [], []

    vecs = embed_chunks(chunks)

    chunk_ids: List[str] = []
    jd_ids:    List[int] = []
    idxs:      List[int] = []
    urls:      List[str] = []

    for i, text in enumerate(chunks):
        cid = f"jd{jd_id}_c{i}"
        key = build_object_key(jd_id, i)
        if save_to_minio and put_object_str:
            put_object_str(key, text)
        chunk_ids.append(cid)
        jd_ids.append(int(jd_id))
        idxs.append(int(i))
        urls.append(key)

    return chunk_ids, jd_ids, idxs, urls, vecs