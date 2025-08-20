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

import re
from typing import List

# Cắt câu đơn giản: sau ., ?, ! (kể cả tiếng Việt) + có ký tự tiếp theo
_SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\!。！？])\s+(?=[^\s])')

def _split_into_units(text: str) -> List[str]:
    """
    Tách văn bản thành các "đơn vị" nhỏ trước khi gom chunk:
    - Ưu tiên tách theo heading markdown (#, ##, ...)
    - Sau đó tách theo đoạn (blank line)
    - Nếu block vẫn dài, tách tiếp theo câu
    """
    lines = text.splitlines()
    blocks: List[str] = []
    buf: List[str] = []

    for ln in lines:
        # heading markdown → đóng block trước đó, mở block mới
        if re.match(r'^\s*#{1,6}\s', ln):
            if buf:
                blocks.append('\n'.join(buf).strip())
                buf = []
            blocks.append(ln.strip())
            continue

        # dòng trống → kết thúc 1 block đoạn
        if ln.strip() == "":
            if buf:
                blocks.append('\n'.join(buf).strip())
                buf = []
            continue

        buf.append(ln)

    if buf:
        blocks.append('\n'.join(buf).strip())

    # Với block quá dài → tách nhỏ theo câu
    units: List[str] = []
    for b in blocks:
        if len(b) <= 800:
            if b:
                units.append(b)
        else:
            sents = _SENT_SPLIT_RE.split(b)
            for s in sents:
                s = s.strip()
                if s:
                    units.append(s)

    return units


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """
    Chunk văn bản theo kích thước ký tự, có overlap, thân thiện Markdown.

    Args:
        text: Nội dung nguồn (Markdown/Plaintext).
        max_chars: Số ký tự tối đa mỗi chunk (>=200).
        overlap: Số ký tự chồng lặp giữa 2 chunk liên tiếp (0..max_chars//2).

    Returns:
        List[str]: Danh sách chunk text.
    """
    text = (text or "").strip()
    if not text:
        return []

    max_chars = max(200, int(max_chars))
    overlap = max(0, min(int(overlap), max_chars // 2))

    units = _split_into_units(text)

    chunks: List[str] = []
    cur = ""

    for u in units:
        if not cur:
            cur = u
            # hard-split nếu đơn vị quá dài ngay từ đầu
            while len(cur) > max_chars:
                head = cur[:max_chars]
                chunks.append(head)
                tail = head[-overlap:] if overlap > 0 else ""
                # tránh cắt giữa từ nếu có thể
                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail
                cur = tail + cur[max_chars:]
            continue

        prospective_len = len(cur) + 1 + len(u)  # +1 do '\n'
        if prospective_len <= max_chars:
            cur = f"{cur}\n{u}"
        else:
            # đẩy chunk hiện tại
            chunks.append(cur)

            # seed chunk tiếp theo bằng phần đuôi overlap
            if overlap > 0 and len(cur) > overlap:
                tail = cur[-overlap:]
                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail
                cur = f"{tail}\n{u}"
            else:
                cur = u

            # nếu vẫn quá dài → hard-split theo cửa sổ
            while len(cur) > max_chars:
                head = cur[:max_chars]
                chunks.append(head)
                tail = head[-overlap:] if overlap > 0 else ""
                tail = tail[tail.find(" ") + 1 :] if (" " in tail) else tail
                cur = tail + cur[max_chars:]

    if cur:
        chunks.append(cur)

    return [c.strip() for c in chunks if c.strip()]