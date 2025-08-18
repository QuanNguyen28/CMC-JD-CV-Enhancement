from __future__ import annotations
from typing import List
import re
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _clean(s: str) -> str:
    s = s or ""
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def split_markdown(md: str, *, max_chars_per_chunk: int = 1200, overlap: int = 150, min_chars: int = 300) -> List[str]:
    """
    Chunk Markdown theo đoạn/heading. ~600–1200 ký tự/chunk, có overlap để giữ ngữ cảnh.
    """
    md = _clean(md)
    if not md:
        return []

    parts = re.split(r"(?:\n\s*\n)|(?:\n(?=#))", md)
    chunks: List[str] = []
    buf = ""
    for p in parts:
        p = _clean(p)
        if not p:
            continue
        if not buf:
            buf = p
        elif len(buf) + 1 + len(p) <= max_chars_per_chunk:
            buf = f"{buf}\n{p}"
        else:
            if len(buf) >= min_chars:
                chunks.append(buf)
            else:
                buf = f"{buf}\n{p}"
                continue
            tail = buf[-overlap:] if overlap > 0 and len(buf) > overlap else ""
            buf = f"{tail}\n{p}" if tail else p
    if buf and len(buf.strip()) >= min_chars:
        chunks.append(buf.strip())

    return [c[:max_chars_per_chunk] for c in chunks if c.strip()]