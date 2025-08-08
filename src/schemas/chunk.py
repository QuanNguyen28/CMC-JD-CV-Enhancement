# src/schemas/chunk.py
from pydantic import BaseModel

class ChunkRequest(BaseModel):
    query: str
    top_k: int = 5

class ChunkResponse(BaseModel):
    text: str
    score: float
