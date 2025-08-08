# src/api/v1/retriever.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from src.schemas.chunk import ChunkRequest, ChunkResponse
from src.services.retriever_service import RetrieverService
from src.api.dependencies import require_roles

router = APIRouter(prefix="/v1/retrieve", tags=["Retrieve"])

@router.post("/similar", response_model=List[ChunkResponse])
def retrieve_similar(
    req: ChunkRequest,
    current_user=Depends(require_roles("recruiter", "admin", "manager"))
):
    """
    Given a query string, return the top-k most semantically similar JD chunks.
    """
    try:
        # Perform retrieval
        results = RetrieverService.retrieve_similar(query=req.query, top_k=req.top_k)
        # Map to response schema
        return [ChunkResponse(text=r["chunk"], score=r["score"]) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")