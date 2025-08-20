# src/db/base.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from src.core.config import DB_SCHEMA  # ví dụ: "smarthire"

# Gắn schema mặc định cho toàn bộ Base
metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)