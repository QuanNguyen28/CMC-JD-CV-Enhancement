# src/utils/local_storage.py
from __future__ import annotations
import os
from typing import Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import CHUNK_LOCAL_DIR

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def make_chunk_path(jd_id: int, chunk_index: int) -> str:
    base = os.path.join(CHUNK_LOCAL_DIR, f"jd-{jd_id}")
    ensure_dir(base)
    return os.path.join(base, f"chunk-{chunk_index}.md")

def write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding=encoding) as f:
        f.write(text or "")

def read_text(path: str, encoding: str = "utf-8") -> Optional[str]:
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception:
        return None