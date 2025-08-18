# src/db/session.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from src.core.config import DATABASE_URL, DB_SCHEMA

# Tạo engine 1 lần
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # tránh stale connections
    future=True              # SQLAlchemy 2.x style
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_engine():
    """Trả về engine dùng cho ETL/DDL."""
    return engine

def get_db():
    """
    Dependency cho FastAPI: tạo Session, set search_path và yield.
    Tự commit/rollback/close an toàn.
    """
    db = SessionLocal()
    try:
        # Nếu bạn dùng schema riêng (vd: 'smarthire'), set search_path mỗi phiên
        if DB_SCHEMA:
            db.execute(text("SET search_path TO :schema, public;"), {"schema": DB_SCHEMA})
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()