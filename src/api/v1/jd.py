# src/api/v1/jd.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from sqlalchemy.orm import Session

from src.schemas.jd import JDGenerateRequest, JDGenerateResponse, JDVersionResponse, JDUpdateRequest
from src.api.dependencies import get_db, require_roles
from src.crud.jd_crud import create_jd
from src.services.role_taxonomy_mapper import get_or_create_family
from src.services.llm_prompt_orchestrator import generate_jd_text
from src.services.jd_versioning_service import get_versions, update_jd
from src.services.export_bridge import export_jd_file

router = APIRouter(prefix="/v1/jd", tags=["JD"])

@router.post("/generate", response_model=JDGenerateResponse)
def create_jd_endpoint(
    req: JDGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    Generate a new Job Description via LLM, store the JD record, and record its version.
    """
    try:
        # Resolve job_family → family_id (optional)
        family_id = get_or_create_family(db, req.job_family) if getattr(req, "job_family", None) else None

        # Insert the JD record and get its ID
        jd_id = create_jd(db, req=req, created_by=current_user.username, family_id=family_id)

        # Prepare metadata for LLM (+ optional RAG chunks)
        chunks_list = (req.chunks or []) if hasattr(req, "chunks") else []
        chunks_text = "\n\n---\n".join([c.strip() for c in chunks_list if c and str(c).strip()])

        metadata = req.model_dump() if hasattr(req, "model_dump") else req.dict()
        metadata.update({
            "jd_id": jd_id,
            "created_by": current_user.username,
            "family_id": family_id,
            "chunks": chunks_list,
            "chunks_text": chunks_text,
        })

        # Generate content and record version
        content_md, version_number = generate_jd_text(metadata, db)

        return JDGenerateResponse(jd_id=jd_id, content_md=content_md, version=version_number)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JD generation failed: {e}"
        )

@router.get("/version-history/{jd_id}", response_model=List[JDVersionResponse])
def version_history(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin", "manager"))
):
    return get_versions(db, jd_id)

@router.put("/update", response_model=dict)
def update_jd_endpoint(
    req: JDUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    Update an existing JD content, record a new version.
    """
    try:
        update_jd(db, req, updated_by=current_user.username)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JD update failed: {e}"
        )

@router.get(
    "/export/{jd_id}",
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}},
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
                    "schema": {"type": "string", "format": "binary"}
                },
            },
            "description": "Binary file download",
        }
    },
)
def export_jd(
    jd_id: int,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin")),
):
    """
    Export a JD as PDF or DOCX (binary). No response_model here.
    """
    if format not in ("pdf", "docx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format")

    data = export_jd_file(db, jd_id, format)
    media = (
        "application/pdf"
        if format == "pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    filename = f"JD_{jd_id}.{format}"
    return Response(
        content=data,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )