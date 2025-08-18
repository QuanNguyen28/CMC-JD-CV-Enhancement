# src/services/export_bridge.py
from typing import Literal
from fastapi import HTTPException
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session

from src.db.models import JobDescription
from src.utils.export import (
    render_markdown_to_docx,
    render_markdown_to_pdf,
)

Format = Literal["pdf", "docx"]

def export_jd_file(db: Session, jd_id: int, fmt: Format = "pdf") -> bytes:
    jd = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")

    title = (jd.title or "").strip()
    md = jd.content_md or ""
    # ghép tiêu đề cho file đẹp hơn
    md_full = f"# {title}\n\n{md}" if title else md

    if fmt == "pdf":
        return render_markdown_to_pdf(md_full)
    elif fmt == "docx":
        return render_markdown_to_docx(md_full)
    else:
        raise HTTPException(status_code=400, detail="Invalid format")