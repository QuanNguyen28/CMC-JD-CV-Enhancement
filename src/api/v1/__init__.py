# src/api/v1/__init__.py
"""
API v1 package initializer: imports all version-1 routers.
"""
from fastapi import APIRouter
from .jd import router as jd_router
from .interview import router as interview_router
from .roles import router as roles_router
from .retriever import router as retriever_router

api_v1 = APIRouter()
api_v1.include_router(retriever_router)

__all__ = [
    "jd_router",
    "interview_router",
    "roles_router",
    "retrieve_router",
]