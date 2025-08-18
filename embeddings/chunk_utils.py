# embeddings/chunk_utils.py
from __future__ import annotations
from typing import List, Tuple
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.utils.gemini_embed import embed_text
from embeddings.utils.chunker import split_markdown
from src.utils.local_storage import make_chunk_path, write_text

def make_chunks(md: str) -> List[str]:
    return split_markdown(md or "")

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    return embed_text(chunks)

def prepare_chunk_records(
    jd_id: int,
    md: str,
    *,
    save_to_local: bool = True
) -> Tuple[List[str], List[int], List[int], List[str], List[List[float]]]:
    """
    Trả về dữ liệu sẵn sàng insert Milvus:
      - chunk_id: "jd{jd_id}_c{idx}"
      - jd_id, chunk_index
      - object_url: đường dẫn file local (data/chunks/jd-<id>/chunk-<n>.md)
      - embedding: vector
    """
    chunks = make_chunks(md)
    if not chunks:
        return [], [], [], [], []

    vecs = embed_chunks(chunks)

    chunk_ids: List[str] = []
    jd_ids:    List[int] = []
    idxs:      List[int] = []
    paths:     List[str] = []

    for i, text in enumerate(chunks):
        cid  = f"jd{jd_id}_c{i}"
        path = make_chunk_path(jd_id, i)
        if save_to_local:
            write_text(path, text)
        chunk_ids.append(cid)
        jd_ids.append(int(jd_id))
        idxs.append(int(i))
        paths.append(path)

    return chunk_ids, jd_ids, idxs, paths, vecs