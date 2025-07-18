# retriever/__init__.py
"""
Retriever package: FastAPI service for semantic search over JD chunks.
"""

# Expose the FastAPI app instance
from .app import app

__all__ = ["app"]
