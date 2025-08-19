# src/services/jd_versioning_service.py
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from src.db.models import JobDescription as JDModel, JDVersion as VerModel
from src.schemas.jd import JDUpdateRequest
from src.utils.export import render_markdown_to_pdf, render_markdown_to_docx


def _get_latest_version_number(db: Session, jd_id: int) -> int:
    """
    Lấy version_number mới nhất trong bảng jd_versions cho JD này.
    """
    v = (
        db.query(VerModel.version_number)
        .filter(VerModel.jd_id == jd_id)
        .order_by(VerModel.version_number.desc())
        .first()
    )
    return (v[0] if v else 0) or 0


def record_jd_version(
    db: Session,
    jd_id: int,
    content_md: str,
    updated_by: str,
    change_summary: Optional[str] = "",
) -> int:
    """
    Ghi nhận một version mới cho JD và cập nhật bản ghi JD hiện hành.
    Trả về version_number mới.
    """
    jd = db.query(JDModel).filter(JDModel.jd_id == jd_id).first()
    if not jd:
        raise ValueError(f"JD {jd_id} not found")

    # Xác định version kế tiếp: lấy max giữa version hiện tại của JD và version trong bảng jd_versions
    latest_from_versions = _get_latest_version_number(db, jd_id)
    base_version = max(jd.version or 0, latest_from_versions or 0)
    next_ver = base_version + 1

    ver = VerModel(
        jd_id=jd_id,
        version_number=next_ver,
        content_md=content_md,
        edited_by=updated_by or "system",
        edited_at=datetime.utcnow(),
        change_summary=change_summary or "auto",
    )
    db.add(ver)

    # Cập nhật bản JD chính
    jd.content_md = content_md
    jd.version = next_ver
    jd.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ver)
    return next_ver


def get_versions(db: Session, jd_id: int):
    """
    Trả về danh sách version theo thứ tự mới → cũ.
    Mapping key khớp với JDVersionResponse:
      - version_number
      - content_md
      - edited_at
      - edited_by
    """
    rows = (
        db.query(VerModel)
        .filter(VerModel.jd_id == jd_id)
        .order_by(VerModel.version_number.desc())
        .all()
    )
    return [
        {
            "version_number": r.version_number,
            "content_md": r.content_md,
            "edited_at": r.edited_at,
            "edited_by": r.edited_by,
        }
        for r in rows
    ]


def update_jd(db: Session, req: JDUpdateRequest, updated_by: str) -> int:
    """
    Ghi version mới khi user cập nhật JD.
    """
    return record_jd_version(
        db=db,
        jd_id=req.jd_id,
        content_md=req.content_md,
        updated_by=updated_by,
        change_summary=getattr(req, "change_summary", "manual update"),
    )


def export_jd_file(db: Session, jd_id: int, fmt: str) -> bytes:
    """
    Render JD hiện hành ra PDF/DOCX.
    """
    jd = db.query(JDModel).filter(JDModel.jd_id == jd_id).first()
    if not jd or not jd.content_md:
        raise ValueError("JD content not found")

    fmt = (fmt or "").lower()
    if fmt == "pdf":
        return render_markdown_to_pdf(jd.content_md)
    elif fmt == "docx":
        return render_markdown_to_docx(jd.content_md)
    else:
        raise ValueError("Invalid format")