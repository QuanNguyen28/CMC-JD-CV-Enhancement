# prompt_generator/__init__.py
"""
Prompt Generator package: FastAPI service for generating Job Descriptions
and Interview Questions via Gemini API, using Jinja2 templates.
"""

# Expose the FastAPI app instance
from .app import app

__all__ = ["app"]
