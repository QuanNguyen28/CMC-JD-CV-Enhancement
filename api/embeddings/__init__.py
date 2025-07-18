# embeddings/__init__.py
"""
Embeddings package: chunking and embedding Job Descriptions into MinIO + Milvus.
"""

from .chunk_utils import chunk_text
from .jd_chunk_embed import main as run_jd_chunk_embed

__all__ = [
    "chunk_text",
    "run_jd_chunk_embed",
]
