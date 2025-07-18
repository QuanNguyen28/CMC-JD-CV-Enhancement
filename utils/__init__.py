# utils/__init__.py
"""
Utils package: shared helper functions (e.g., Gemini embedding, file extraction).
"""

from .gemini_embed import embed_text

__all__ = ["embed_text"]
