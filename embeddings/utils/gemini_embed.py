# src/embeddings/utils/gemini_embed.py
from __future__ import annotations
from typing import List
import math

import google.generativeai as genai

from src.core.config import (
    GEMINI_API_KEY,
    GEMINI_EMBED_MODEL,
    VECTOR_DIM,
)

# Cấu hình Gemini 1 lần từ config.py
if not GEMINI_API_KEY:
    # Chủ động cảnh báo, để dev biết cấu hình chưa đúng
    print("⚠️  GEMINI_API_KEY is not set. Embedding will fail if called.")
else:
    genai.configure(api_key=GEMINI_API_KEY)


def _l2_norm(v: List[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v)) or 1.0


def _unit_normalize(v: List[float]) -> List[float]:
    n = _l2_norm(v)
    return [float(x) / n for x in v]


def _fix_dim(vec: List[float], dim: int) -> List[float]:
    """
    Đề phòng model thay đổi kích thước: cắt/pad về đúng VECTOR_DIM.
    (Sau đó normalize lại để dùng COSINE ổn định.)
    """
    if len(vec) == dim:
        return vec
    if len(vec) > dim:
        return vec[:dim]
    return vec + [0.0] * (dim - len(vec))


def embed_text(
    chunks: List[str],
    model: str = GEMINI_EMBED_MODEL,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> List[List[float]]:
    """
    Embed danh sách đoạn văn bản bằng Gemini.
    - Trả về list vector đã FIX_DIM + UNIT-NORMALIZE (phù hợp search COSINE).
    - Giữ API và log tương tự style bạn gửi.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY in your environment.")

    print(f"INFO: Embedding {len(chunks)} chunks using model '{model}'...")
    try:
        embeddings: List[List[float]] = []

        # Thư viện google.generativeai hiện ổn định cho embed từng content một.
        # (Một số version hỗ trợ batch nhưng không nhất quán -> iterate an toàn.)
        for i, text in enumerate(chunks):
            resp = genai.embed_content(
                model=model,
                content=text or "",
                task_type=task_type,
            )
            vec = resp["embedding"]
            vec = _unit_normalize(_fix_dim(vec, VECTOR_DIM))
            embeddings.append(vec)

        print(f"✅ Successfully generated {len(embeddings)} embeddings.")
        return embeddings

    except Exception as e:
        print(f"❌ An error occurred during the Gemini API call: {e}")
        raise


def embed_query(
    query: str,
    model: str = GEMINI_EMBED_MODEL,
    task_type: str = "RETRIEVAL_QUERY",
) -> List[float]:
    """
    Tiện ích embed cho 1 query (unit-normalized).
    """
    [vec] = embed_text([query], model=model, task_type=task_type)
    return vec