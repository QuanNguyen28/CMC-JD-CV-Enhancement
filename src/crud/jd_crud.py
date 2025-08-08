# src/crud/jd_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import re
from uuid import uuid4

from src.db.models import JobFamily as JFModel, JobDescription as JDModel
from src.schemas.jd import JDGenerateRequest

def slugify(text_: str) -> str:
    s = text_.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def gen_job_code(title: str) -> str:
    base = slugify(title) or "role"
    # Thêm 6 ký tự random để tránh trùng (UNIQUE)
    return f"{base}-{uuid4().hex[:6]}"

def get_or_create_family(db: Session, family_name: str) -> int:
    fam = db.query(JFModel).filter(JFModel.name == family_name).first()
    if not fam:
        fam = JFModel(name=family_name)
        db.add(fam)
        db.commit()
        db.refresh(fam)
    return fam.family_id

def create_jd(
    db: Session,
    req: JDGenerateRequest,
    created_by: Optional[str] = None,
    family_id: Optional[int] = None
) -> int:
    """
    Insert JD using raw SQL and RETURNING jd_id.
    Tự sinh job_code để thỏa mãn NOT NULL + UNIQUE.
    """
    job_code = gen_job_code(req.title)

    result = db.execute(
        text("""
            INSERT INTO job_descriptions
              (job_code, title, department, family_id, level, employment_type, location, content_md, version, created_by, created_at, updated_at)
            VALUES
              (:job_code, :title, :department, :family_id, :level, :employment_type, :location, :content_md, :version, :created_by, NOW(), NULL)
            RETURNING jd_id
        """),
        {
            "job_code": job_code,
            "title": req.title,
            "department": req.department,
            "family_id": family_id,
            "level": req.level,              # khớp schema request
            "employment_type": None,
            "location": None,
            "content_md": "",
            "version": 1,
            "created_by": created_by,
        }
    )
    new_id = result.scalar_one()
    db.commit()
    return new_id

def get_jd_content(db: Session, jd_id: int) -> str:
    jd = db.query(JDModel).filter(JDModel.jd_id == jd_id).first()
    return jd.content_md if jd else ""

def list_all_jds(db: Session) -> List[JDModel]:
    return db.query(JDModel).all()