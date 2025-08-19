# src/api/v1/retriever.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.api.dependencies import require_roles
from src.services.retriever_service import (
    RetrieveSimilarReq, RetrieveReq, ChunkResult,
    retrieve_similar, retrieve_with_snippet
)
from embeddings.utils.gemini_embed import embed_text  # hàm tạo vector từ query

router = APIRouter(prefix="/v1/retrieve", tags=["Retriever"])

@router.post("/similar", response_model=List[ChunkResult])
def retrieve_similar_endpoint(req: RetrieveSimilarReq, _: str = Depends(require_roles("recruiter","manager","admin"))):
    try:
        qvec = embed_text([req.query])[0]
        return retrieve_similar(qvec, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

@router.post("", response_model=List[ChunkResult])
def retrieve_endpoint(req: RetrieveReq, _: str = Depends(require_roles("recruiter","manager","admin"))):
    try:
        qvec = embed_text([req.query])[0]
        return retrieve_with_snippet(qvec, req.top_k, req.snippet_lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")