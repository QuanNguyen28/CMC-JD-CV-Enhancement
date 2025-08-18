# embeddings/jd_chunk_embed.py
from __future__ import annotations
from typing import List
from pymilvus import Collection
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.db.models import JobDescription
from embeddings.chunk_utils import prepare_chunk_records
from embeddings.schema import connect, ensure_collection, FIELD_JD_ID, COLLECTION_NAME

def _delete_existing_jd(col: Collection, jd_id: int):
    try:
        col.delete(expr=f"{FIELD_JD_ID} == {int(jd_id)}")
    except Exception:
        pass

def reindex_jd(jd_id: int, *, save_to_local: bool = True) -> int:
    connect()
    col = ensure_collection()

    db: Session = SessionLocal()
    try:
        row = db.query(JobDescription).filter(JobDescription.jd_id == jd_id).first()
        if not row or not (row.content_md and row.content_md.strip()):
            return 0

        _delete_existing_jd(col, jd_id)

        chunk_ids, jd_ids, idxs, paths, vecs = prepare_chunk_records(
            jd_id=row.jd_id,
            md=row.content_md,
            save_to_local=save_to_local,
        )
        if not chunk_ids:
            return 0

        col.insert([chunk_ids, jd_ids, idxs, paths, vecs])
        col.flush()
        try:
            col.load()
        except Exception:
            pass
        return len(chunk_ids)
    finally:
        db.close()

def reindex_all(*, save_to_local: bool = True) -> int:
    connect()
    col = ensure_collection()

    db: Session = SessionLocal()
    total = 0
    try:
        rows: List[JobDescription] = db.query(JobDescription.jd_id, JobDescription.content_md).all()
        for jd_id, md in rows:
            if not (md and md.strip()):
                continue
            _delete_existing_jd(col, jd_id)

            chunk_ids, jd_ids, idxs, paths, vecs = prepare_chunk_records(
                jd_id=jd_id,
                md=md,
                save_to_local=save_to_local,
            )
            if not chunk_ids:
                continue

            col.insert([chunk_ids, jd_ids, idxs, paths, vecs])
            total += len(chunk_ids)

        col.flush()
        try:
            col.load()
        except Exception:
            pass
        print(f"[Milvus] Inserted {total} chunks into '{COLLECTION_NAME}'")
        return total
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reindex JD content into Milvus")
    parser.add_argument("--only", type=int, help="Reindex only this jd_id")
    parser.add_argument("--no-save", action="store_true", help="Không ghi raw chunk xuống local")
    args = parser.parse_args()

    if args.only:
        cnt = reindex_jd(args.only, save_to_local=not args.no_save)
        print(f"Reindexed JD {args.only}: {cnt} chunks")
    else:
        total = reindex_all(save_to_local=not args.no_save)
        print(f"Reindexed ALL: {total} chunks")