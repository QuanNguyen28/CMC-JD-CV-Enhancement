# etl/jd_taxonomy_etl.py
from __future__ import annotations
import os
import json
from typing import List, Optional
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.db.models import JobFamily, JDTag

FAMILY_FILE = os.getenv("JD_FAMILIES_FILE", "etl/taxonomy/families.txt")
TAGS_FILE   = os.getenv("JD_TAGS_FILE", "etl/taxonomy/tags.txt")
TAGS_JSON   = os.getenv("JD_TAGS_JSON", "etl/taxonomy/tags.json")  

def _read_lines(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        return []

def seed_families(db: Session, names: List[str]) -> int:
    inserted = 0
    for name in names:
        if not db.query(JobFamily).filter(JobFamily.name == name).first():
            db.add(JobFamily(name=name, description=None))
            inserted += 1
    if inserted:
        db.commit()
    return inserted

def _ensure_tag(db: Session, name: str, parent_id: Optional[int]) -> int:
    row = db.query(JDTag).filter(JDTag.tag_name == name).first()
    if row:
        return row.tag_id
    t = JDTag(tag_name=name, description=None, parent_tag_id=parent_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t.tag_id

def seed_tags_flat(db: Session, names: List[str]) -> int:
    before = db.query(JDTag).count()
    for n in names:
        _ensure_tag(db, n, None)
    return db.query(JDTag).count() - before

def seed_tags_hier(db: Session, nodes: List[dict]) -> int:
    before = db.query(JDTag).count()

    def walk(node: dict, parent: Optional[int]):
        this_id = _ensure_tag(db, node["name"], parent)
        for ch in node.get("children", []) or []:
            walk(ch, this_id)

    for n in nodes:
        walk(n, None)

    return db.query(JDTag).count() - before

def run_seed():
    db: Session = SessionLocal()
    try:
        fams = _read_lines(FAMILY_FILE)
        if fams:
            n = seed_families(db, fams)
            print(f"[TAXO-ETL] Seeded families: +{n}")

        if os.path.exists(TAGS_JSON):
            with open(TAGS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f) or []
            n = seed_tags_hier(db, data)
            print(f"[TAXO-ETL] Seeded tags (hier): +{n}")
        else:
            tags = _read_lines(TAGS_FILE)
            if tags:
                n = seed_tags_flat(db, tags)
                print(f"[TAXO-ETL] Seeded tags (flat): +{n}")

        print("[TAXO-ETL] Done.")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()