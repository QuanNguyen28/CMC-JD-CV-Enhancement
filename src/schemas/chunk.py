# src/schemas/chunk.py
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional

class ChunkRequest(BaseModel):
    query: str
    top_k: int = 5

class ChunkResponse(BaseModel):
    text: str
    score: float

class ChunkUpsert(BaseModel):
    jd_id: int
    texts: List[str]                  # danh sách chunk text (nếu upsert thủ công)
    save_to_minio: Optional[bool] = True

class ChunkDoc(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    object_url: str

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5
    exclude_jd_ids: Optional[List[int]] = NotImplemented
    family_id: Optional[int] = None

class ChunkResult(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    object_path: str
    score: float 

