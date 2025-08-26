# src/schemas/retriever.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=100)
    with_snippet: bool = False

class ChunkHit(BaseModel):
    chunk_id: str
    jd_id: Optional[int] = None
    chunk_index: Optional[int] = None
    object_path: str
    score: float
    snippet: Optional[str] = None

class RetrieveResponse(BaseModel):
    items: List[ChunkHit]


class RetrieveSimilarReq(BaseModel):
    query: str
    top_k: int = 5

class RetrieveReq(BaseModel):
    query: str
    top_k: int = 5
    snippet_lines: int = 8  

class ChunkResult(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    score: float
    object_path: Optional[str] = None
    snippet: Optional[str] = None