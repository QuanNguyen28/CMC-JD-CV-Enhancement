#!/usr/bin/env python3
"""
Kiểm tra kết nối tới:
- PostgreSQL (RDS) qua SQLAlchemy engine của app
- Milvus qua pymilvus

Cách chạy:
  python scripts/check_connectivity.py                 # kiểm cả 2
  python scripts/check_connectivity.py --postgres      # chỉ Postgres
  python scripts/check_connectivity.py --milvus        # chỉ Milvus
"""
from __future__ import annotations
import argparse
from contextlib import suppress
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Postgres (SQLAlchemy) ---
from sqlalchemy import text
from src.db.session import engine
from src.core.config import DB_HOST, DB_PORT, DB_NAME

# --- Milvus ---
from pymilvus import connections, utility, Collection
from embeddings.schema import (
    COLLECTION_NAME,
    FIELD_JD_ID,
)
from src.core.config import MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION


def check_postgres() -> bool:
    print("== Checking PostgreSQL (RDS) ==")
    print(f"Target: host={DB_HOST} port={DB_PORT} db={DB_NAME}")
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT 1 as ok, version()")).first()
            if not row or row[0] != 1:
                print("PostgreSQL: FAIL (no row)")
                return False
            print(f"PostgreSQL: OK  | version = {row[1]}")
            # Thử query nhẹ từ bảng chính (nếu có)
            with suppress(Exception):
                count = conn.execute(text("SELECT COUNT(*) FROM job_descriptions")).scalar()
                print(f"job_descriptions: {count} rows")
            return True
    except Exception as e:
        print(f"PostgreSQL: FAIL | {e}")
        return False


def check_milvus() -> bool:
    print("\n== Checking Milvus ==")
    print(f"Target: host={MILVUS_HOST} port={MILVUS_PORT} collection={MILVUS_COLLECTION}")
    try:
        connections.disconnect("default")
    except Exception:
        pass

    try:
        connections.connect("default", host=MILVUS_HOST, port=str(MILVUS_PORT))
        ver = utility.get_server_version()
        print(f"Milvus: OK | server_version = {ver}")

        # Liệt kê collection & kiểm tra collection app (không tạo mới)
        cols = utility.list_collections()
        print(f"Collections: {cols}")
        if MILVUS_COLLECTION in cols:
            col = Collection(COLLECTION_NAME)
            # load nhẹ để đọc num_entities (có thể bỏ nếu không muốn)
            with suppress(Exception):
                col.load()
            print(f"Collection '{COLLECTION_NAME}' entities = {col.num_entities}")
            # thử query rất nhẹ (nếu có dữ liệu)
            with suppress(Exception):
                res = col.query(expr=f"{FIELD_JD_ID} > 0", output_fields=[FIELD_JD_ID], limit=1)
                print(f"Sample query: {res}")
        else:
            print(f"Warning: collection '{COLLECTION_NAME}' chưa tồn tại (OK nếu bạn chưa reindex).")
        return True
    except Exception as e:
        print(f"Milvus: FAIL | {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--postgres", action="store_true", help="Chỉ kiểm PostgreSQL")
    ap.add_argument("--milvus", action="store_true", help="Chỉ kiểm Milvus")
    args = ap.parse_args()

    do_pg = args.postgres or not (args.postgres or args.milvus)
    do_mv = args.milvus or not (args.postgres or args.milvus)

    ok = True
    if do_pg:
        ok &= check_postgres()
    if do_mv:
        ok &= check_milvus()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()