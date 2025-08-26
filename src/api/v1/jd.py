# src/api/v1/jd.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from typing import List
from sqlalchemy.orm import Session

from src.schemas.jd import JDGenerateRequest, JDGenerateResponse, JDVersionResponse, JDUpdateRequest
from src.api.dependencies import get_db, require_roles
from src.crud.jd_crud import create_jd
from src.services.role_taxonomy_mapper import get_or_create_family
from src.services.llm_prompt_orchestrator import generate_jd_text
from src.services.jd_versioning_service import get_versions, update_jd
from src.services.export_bridge import export_jd_file

from embeddings.utils.gemini_embed import embed_text
from src.services.retriever_service import retrieve_with_snippet
from fastapi.responses import StreamingResponse
from src.schemas.jd_live import (
    JDImproveRequest, JDImproveResponse,
    JDSuggestRequest, JDSuggestResponse
)
from src.services.llm_prompt_orchestrator import (
    improve_jd, suggest_jd_section, fake_streaming
)
from src.services.jd_versioning_service import record_jd_version

router = APIRouter(prefix="/v1/jd", tags=["JD"])

def _format_chunks_text(chunks, max_chars: int = 3500) -> str:
    """
    Join snippet/metadata into a compact context block for the LLM prompt.
    """
    lines = []
    for i, c in enumerate(chunks, 1):
        head = f"[{i}] JD#{getattr(c, 'jd_id', 0)} – chunk#{getattr(c, 'chunk_index', 0)} (score={getattr(c, 'score', 0.0):.3f})"
        body = (getattr(c, 'snippet', None) or "").strip()
        if not body:
            # fallback: put metadata so LLM still knows the source
            body = f"(No snippet; source_path={getattr(c, 'object_path', None) or 'N/A'})"
        lines.append(head + "\n" + body)
    text = "\n\n".join(lines)
    return text[:max_chars]

@router.post("/generate", response_model=JDGenerateResponse)
def create_jd_endpoint(
    req: JDGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin")),
    use_rag: bool = Query(True, description="Use Milvus RAG for prompt enrichment"),
    top_k: int = Query(5, ge=1, le=20, description="Top-K similar chunks"),
    snippet_lines: int = Query(12, ge=1, le=100, description="Lines to preview from each chunk file")
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
        # 1) User-provided chunks (if any)
        user_chunks_list = (req.chunks or []) if hasattr(req, "chunks") else []
        user_chunks_text = "\n\n---\n".join([str(c).strip() for c in user_chunks_list if c and str(c).strip()])

        # 2) RAG from Milvus
        rag_chunks_text = ""
        if use_rag:
            # Build semantic query from request fields
            q_parts = [req.title or ""]
            if getattr(req, "department", None):
                q_parts.append(req.department)
            level_val = getattr(req, "level", None) or getattr(req, "seniority", None)
            if level_val:
                q_parts.append(level_val)
            if getattr(req, "job_family", None):
                q_parts.append(req.job_family)
            query = " | ".join([p for p in q_parts if p]).strip()

            if query:
                try:
                    vec = embed_text([query])[0]  # 1-D embedding vector
                    hits = retrieve_with_snippet(vec, top_k=top_k, snippet_lines=snippet_lines)
                    rag_chunks_text = _format_chunks_text(hits)
                except Exception as e:
                    # Non-fatal: continue without RAG if vector search fails
                    rag_chunks_text = ""

        # 3) Merge both (user chunks first, then RAG)
        chunks_text_parts = [s for s in [user_chunks_text, rag_chunks_text] if s]
        chunks_text = "\n\n---\n".join(chunks_text_parts)

        metadata = req.model_dump() if hasattr(req, "model_dump") else req.dict()
        metadata.update({
            "jd_id": jd_id,
            "created_by": current_user.username,
            "family_id": family_id,
            "chunks": user_chunks_list,
            "chunks_text": chunks_text,
            # keep both keys for template compatibility
            "level": getattr(req, "level", None) or getattr(req, "seniority", None) or "",
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

@router.post("/improve", response_model=JDImproveResponse)
def improve_jd_endpoint(
    req: JDImproveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    Cải thiện toàn văn JD theo chỉ dẫn. Có thể lưu thành version mới nếu `create_new_version=True`.
    """
    try:
        improved = improve_jd(req.content_md, req.instruction, req.language)
        ver = None
        if req.create_new_version:
            # Cần jd_id để lưu; nếu client không gửi jd_id thì bỏ qua lưu version.
            # Gợi ý: client gửi kèm jd_id trong query hoặc body nếu muốn lưu.
            # Ở đây mình thử lấy jd_id từ phần header tạm (tuỳ bạn thay đổi).
            jd_id = None
            # Nếu muốn chuẩn, hãy thêm jd_id vào JDImproveRequest và dùng ở đây.
            if jd_id:
                ver = record_jd_version(
                    db,
                    jd_id=jd_id,
                    content_md=improved,
                    updated_by=current_user.username,
                    change_summary="improve via /v1/jd/improve"
                )
        return JDImproveResponse(content_md=improved, version=ver)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improve failed: {e}")

@router.post("/suggest", response_model=JDSuggestResponse)
def suggest_jd_endpoint(
    req: JDSuggestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    Gợi ý bullets/đoạn cho một section cụ thể.
    Có thể truyền thêm chunks_text (đã ghép sẵn từ RAG) để LLM bám theo.
    """
    try:
        out = suggest_jd_section(
            content_md=req.content_md,
            section=req.section or "",
            goal=req.goal or "",
            language=req.language or "vi",
            chunks_text=req.chunks_text or "",
        )
        return JDSuggestResponse(suggestions=out["bullets"], rationale=out.get("rationale"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggest failed: {e}")

@router.post("/improve/stream")
def improve_stream(
    req: JDImproveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    SSE endpoint “giả streaming” (server chunk) để hiển thị live suggestion.
    Client: fetch('/v1/jd/improve/stream', {method:'POST', body:..., headers:{'Accept':'text/event-stream'}})
    """
    try:
        improved = improve_jd(req.content_md, req.instruction, req.language)
        return StreamingResponse(fake_streaming(improved), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improve stream failed: {e}")