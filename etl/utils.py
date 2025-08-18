# etl/utils.py
from __future__ import annotations
from typing import Tuple, Dict, List
import os
import re
import glob
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml  # optional, để parse front-matter
except Exception:
    yaml = None  # type: ignore


def list_md_files(root: str, recursive: bool = False) -> List[str]:
    """
    Liệt kê file .md theo yêu cầu:
    - Mặc định KHÔNG đệ quy (đặt recursive=False).
    - Bật --recursive khi chạy nếu muốn quét sâu.
    """
    root_abs = os.path.abspath(root)
    pattern = os.path.join(root_abs, "**", "*.md") if recursive else os.path.join(root_abs, "*.md")
    files = glob.glob(pattern, recursive=recursive)
    print(f"[JD-ETL] Scanning: {root_abs} -> {len(files)} .md files (recursive={recursive})")
    return files


def read_text(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def parse_front_matter(md: str) -> Tuple[Dict, str]:
    """
    Front-matter YAML:
    ---
    title: ...
    department: ...
    job_family: ...
    level: ...
    tags: [python, api]
    ---
    <markdown body>
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md, flags=re.DOTALL)
    if not m:
        return {}, md.strip()
    raw_meta, body = m.group(1), m.group(2)
    meta: Dict = {}
    if yaml:
        try:
            meta = yaml.safe_load(raw_meta) or {}
        except Exception:
            meta = {}
    else:
        for line in raw_meta.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body.strip()


_slug_re = re.compile(r"[^a-z0-9]+")
def slugify(s: str, max_len: int = 64) -> str:
    s = (s or "").lower().strip()
    s = _slug_re.sub("-", s)
    s = s.strip("-")
    return s[:max_len] if s else "untitled"