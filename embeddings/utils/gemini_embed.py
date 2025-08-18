# src/embeddings/utils/gemini_embed.py
from __future__ import annotations
from typing import List
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import math

import google.generativeai as genai

from src.core.config import (
    GEMINI_API_KEY,
    GEMINI_EMBED_MODEL,
    VECTOR_DIM,
)

# Optional debug similar to the old style (toggle via ENV)
GEMINI_DEBUG = os.getenv("GEMINI_DEBUG", "false").lower() == "true"

if GEMINI_DEBUG:
    key_mask = (
        f"{GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-4:]}" if GEMINI_API_KEY else "None"
    )
    print(f"[GEMINI] model={GEMINI_EMBED_MODEL} dim={VECTOR_DIM} api_key={key_mask}")

# Configure Gemini once via config.py
if not GEMINI_API_KEY:
    # Proactive warning so devs see misconfig instantly
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
    Guard in case model/vector dim changes: trim/pad to VECTOR_DIM,
    then normalize for stable COSINE search.
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
    Embed a list of text chunks with Gemini.
    Returns vectors that are FIXED to VECTOR_DIM and UNIT-NORMALIZED
    (ideal for COSINE similarity in Milvus).
    Keeps logs similar to your older style.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured. Set GEMINI_API_KEY in your environment.")

    if GEMINI_DEBUG:
        print(f"INFO: Embedding {len(chunks)} chunks using model '{model}'...")

    try:
        embeddings: List[List[float]] = []

        # Safer across library versions: iterate per content.
        for i, text in enumerate(chunks):
            resp = genai.embed_content(
                model=model,
                content=text or "",
                task_type=task_type,
            )
            vec = resp["embedding"]
            vec = _unit_normalize(_fix_dim(vec, VECTOR_DIM))
            embeddings.append(vec)

        if GEMINI_DEBUG:
            print(f"✅ Successfully generated {len(embeddings)} embeddings.")
        return embeddings

    except Exception as e:
        print(f"❌ Gemini embed error: {e}")
        raise


def embed_query(
    query: str,
    model: str = GEMINI_EMBED_MODEL,
    task_type: str = "RETRIEVAL_QUERY",
) -> List[float]:
    """Convenience wrapper for single query (unit-normalized)."""
    [vec] = embed_text([query], model=model, task_type=task_type)
    return vec