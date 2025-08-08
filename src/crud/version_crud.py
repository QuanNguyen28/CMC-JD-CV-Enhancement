# src/crud/version_crud.py
from sqlalchemy.orm import Session
from src.db.models import JDVersion as VersionModel
from datetime import datetime
from typing import List

def create_version(db: Session, jd_id: int, content_md: str, updated_by: str, timestamp: datetime) -> int:
    version = VersionModel(
        jd_id=jd_id,
        content_md=content_md,
        updated_by=updated_by,
        updated_at=timestamp
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version.version

def get_versions_by_jd_id(db: Session, jd_id: int) -> List[VersionModel]:
    return db.query(VersionModel).filter(VersionModel.jd_id == jd_id).order_by(VersionModel.version).all()

def get_all_chunks(db: Session):
    # Assuming chunks are stored in VersionModel.content_md split
    versions = db.query(VersionModel).all()
    chunks = []
    for v in versions:
        for chunk in v.content_md.split("\n\n"):
            # Dummy vector placeholder
            chunks.append({"text": chunk, "vector": []})
    return chunks