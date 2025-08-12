# src/api/v1/retriever.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, require_roles
from src.services.retriever_service import semantic_retrieve

router = APIRouter(prefix="/v1/retrieve", tags=["Retriever"])

# ====== Schemas ======
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


# ====== Endpoints ======
@router.post(
    "",
    response_model=List[ChunkResult],
    dependencies=[Depends(require_roles("recruiter", "manager", "admin"))],
)
@router.post(
    "/similar",
    response_model=List[ChunkResult],
    dependencies=[Depends(require_roles("recruiter", "manager", "admin"))],
)
def retrieve_endpoint(
    req: RetrieveRequest,
    db: Session = Depends(get_db),
):
    """
    Semantic retrieve over Milvus using COSINE.
    - Embed query (unit-normalized) -> Milvus search (anns_field='embedding')
    - Trả về: chunk_id, jd_id, chunk_index, object_url, score(similarity)
    - Nếu muốn trả snippet: bật trong service và thêm field vào ChunkResult.
    """
    try:
        if not req.query or not req.query.strip():
            raise HTTPException(status_code=400, detail="Query is required")

        results = semantic_retrieve(
            db=db,
            query=req.query.strip(),
            top_k=max(1, req.top_k),
            prefer_minio=bool(req.prefer_minio),
        )
        if not results:
            # không coi là lỗi; bạn có thể đổi thành 404 nếu muốn
            return []

        # Map dict -> Pydantic model (nếu service đã khớp key, có thể return thẳng)
        return [ChunkResult(**r) for r in results]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")