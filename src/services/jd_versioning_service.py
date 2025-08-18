# src/services/jd_versioning_service.py
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session

from src.db.models import JobDescription as JDModel, JDVersion as VerModel
from src.schemas.jd import JDUpdateRequest

def _get_latest_version_number(db: Session, jd_id: int) -> int:
    v = (
        db.query(VerModel.version_number)
        .filter(VerModel.jd_id == jd_id)
        .order_by(VerModel.version_number.desc())
        .first()
    )
    return v[0] if v else 0

def record_jd_version(db: Session, content_md: str, metadata: dict) -> int:
    """
    Tạo 1 version mới cho JD và cập nhật bản ghi JD chính.
    metadata yêu cầu có: jd_id, created_by (hoặc edited_by)
    """
    jd_id = metadata["jd_id"]
    editor = metadata.get("created_by") or metadata.get("edited_by") or "system"
    change_summary = metadata.get("change_summary")

    next_ver = _get_latest_version_number(db, jd_id) + 1

    ver = VerModel(
        jd_id=jd_id,
        version_number=next_ver,
        content_md=content_md,
        edited_by=editor,
        edited_at=datetime.utcnow(),
        change_summary=change_summary,
    )
    db.add(ver)

    # cập nhật JD chính
    jd = db.query(JDModel).filter(JDModel.jd_id == jd_id).first()
    if jd:
        jd.content_md = content_md
        jd.version = next_ver
        jd.updated_at = datetime.utcnow()

    db.commit()
    return next_ver

def get_versions(db: Session, jd_id: int):
    """
    Trả về danh sách version theo thứ tự mới → cũ.
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

def update_jd(db: Session, req: JDUpdateRequest, updated_by: str):
    """
    Ghi version mới khi user cập nhật JD.
    """
    metadata = {
        "jd_id": req.jd_id,
        "edited_by": updated_by,
        "change_summary": req.change_summary,
    }
    # Lấy nội dung mới từ req.content_md và ghi version
    return record_jd_version(db, req.content_md, metadata)