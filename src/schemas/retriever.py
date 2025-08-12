# src/schemas/retriever.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5
    prefer_minio: Optional[bool] = False

class ChunkResult(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    object_url: str
    score: float
    # snippet: Optional[str] = None  # bật nếu service trả kèm