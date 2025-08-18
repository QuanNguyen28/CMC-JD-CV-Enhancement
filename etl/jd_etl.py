# etl/jd_etl.py
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import delete

# Bảo đảm import được "src" khi chạy file trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.session import SessionLocal
from src.db.models import JobDescription, JobFamily, JDVersion, JDTag, JDTagMap
from etl.utils import list_md_files, read_text, parse_front_matter, slugify

# Thư mục chứa JD mẫu (.md) — mặc định: etl/jd_markdown cạnh repo
DEFAULT_JD_DIR = PROJECT_ROOT / "etl" / "jd_markdown"
JD_DIR = os.getenv("JD_ETL_DIR", str(DEFAULT_JD_DIR))


# ----------------- Helpers DB -----------------
def get_or_create_family(db: Session, family_name: Optional[str]) -> Optional[int]:
    if not family_name:
        return None
    row = db.query(JobFamily).filter(JobFamily.name == family_name).first()
    if row:
        return row.family_id
    row = JobFamily(name=family_name, description=None)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row.family_id


def get_or_create_tag(db: Session, tag_name: str) -> int:
    t = db.query(JDTag).filter(JDTag.tag_name == tag_name).first()
    if t:
        return t.tag_id
    t = JDTag(tag_name=tag_name, description=None, parent_tag_id=None)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t.tag_id


def replace_tag_map(db: Session, jd_id: int, tags: List[str]) -> None:
    db.execute(delete(JDTagMap).where(JDTagMap.jd_id == jd_id))
    db.commit()
    for name in tags:
        tag_id = get_or_create_tag(db, name)
        db.add(JDTagMap(jd_id=jd_id, tag_id=tag_id))
    db.commit()


def insert_version(
    db: Session,
    jd_id: int,
    version_number: int,
    content_md: str,
    edited_by: str,
    change_summary: Optional[str],
) -> None:
    ver = JDVersion(
        jd_id=jd_id,
        version_number=version_number,
        content_md=content_md,
        edited_by=edited_by,
        edited_at=datetime.utcnow(),
        change_summary=change_summary or "ETL import/update",
    )
    db.add(ver)
    db.commit()


# ----------------- Core ETL -----------------
def upsert_jd_from_markdown(
    db: Session,
    *,
    path: str,
    author: str = "etl",
    with_tags: bool = True,
    change_summary: Optional[str] = None,
    update_existing: bool = True,
) -> int:
    """
    Upsert 1 JD từ file .md:
    - Nếu tồn tại (theo job_code) → cập nhật content_md, tăng version, ghi jd_versions.
    - Nếu chưa → tạo mới version=1 + ghi jd_versions(1).
    """
    raw = read_text(path)
    meta, body = parse_front_matter(raw)

    title      = meta.get("title") or os.path.splitext(os.path.basename(path))[0]
    department = meta.get("department")
    level      = meta.get("level")
    family     = meta.get("job_family")
    tags       = meta.get("tags") or []

    # Chuẩn hoá tags
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t).strip() for t in tags if str(t).strip()]
    else:
        tags = []

    family_id  = get_or_create_family(db, family)
    job_code   = slugify(meta.get("title") or os.path.basename(path))

    row = db.query(JobDescription).filter(JobDescription.job_code == job_code).first()
    if row:
        if not update_existing:
            print(f"[JD-ETL] Skip existing: {job_code}")
            return row.jd_id

        row.title      = title
        row.department = department
        row.family_id  = family_id
        row.level      = level
        row.content_md = body
        row.version    = (row.version or 1) + 1
        row.updated_at = datetime.utcnow()
        db.commit()

        insert_version(db, row.jd_id, row.version, body, author, change_summary)
        if with_tags:
            replace_tag_map(db, row.jd_id, tags)
        print(f"[JD-ETL] Updated jd_id={row.jd_id} ({job_code}) v={row.version}")
        return row.jd_id

    # Create mới
    new = JobDescription(
        job_code=job_code,
        title=title,
        department=department,
        family_id=family_id,
        level=level,
        employment_type=None,
        location=None,
        content_md=body,
        version=1,
        created_by=author,
        created_at=datetime.utcnow(),
        updated_at=None,
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    insert_version(db, new.jd_id, 1, body, author, change_summary)
    if with_tags:
        replace_tag_map(db, new.jd_id, tags)
    print(f"[JD-ETL] Inserted jd_id={new.jd_id} ({job_code}) v=1")
    return new.jd_id


def run_etl(
    root: str = JD_DIR,
    *,
    author: str = "etl",
    update_existing: bool = True,
    with_tags: bool = True,
    change_summary: Optional[str] = None,
    only: Optional[str] = None,
    recursive: bool = False,  # mặc định KHÔNG đệ quy
) -> int:
    db: Session = SessionLocal()
    processed = 0
    try:
        files = [only] if only else list_md_files(root, recursive=recursive)
        for p in files:
            try:
                upsert_jd_from_markdown(
                    db,
                    path=p,
                    author=author,
                    with_tags=with_tags,
                    change_summary=change_summary,
                    update_existing=update_existing,
                )
                processed += 1
            except Exception as e:
                print(f"[JD-ETL] ERROR file={p}: {e}")
        print(f"[JD-ETL] Done. processed={processed} files")
        return processed
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="ETL JD markdown -> Postgres (job_descriptions + jd_versions + jd_tag_map)")
    ap.add_argument("--dir", type=str, default=JD_DIR, help="Thư mục JD .md (mặc định: etl/jd_markdown)")
    ap.add_argument("--author", type=str, default="etl")
    ap.add_argument("--no-update", action="store_true", help="Không cập nhật JD đã tồn tại (skip)")
    ap.add_argument("--no-tags", action="store_true", help="Không ghi JD tag map")
    ap.add_argument("--summary", type=str, default=None, help="change_summary cho jd_versions")
    ap.add_argument("--only", type=str, help="Chỉ ETL 1 file cụ thể")
    ap.add_argument("--recursive", action="store_true", help="Quét đệ quy **/*.md (mặc định: chỉ *.md ở gốc)")
    args = ap.parse_args()

    run_etl(
        root=args.dir,
        author=args.author,
        update_existing=not args.no_update,
        with_tags=not args.no_tags,
        change_summary=args.summary,
        only=args.only,
        recursive=args.recursive,
    )