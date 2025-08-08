# src/api/auth/__init__.py
"""
Authentication subpackage initializer
"""
from .auth import router as auth_router

__all__ = ["auth_router"]