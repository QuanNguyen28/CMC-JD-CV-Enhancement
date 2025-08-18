# src/schemas/jd.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JDGenerateRequest(BaseModel):
    title: str
    department: Optional[str] = None
    level: Optional[str] = None
    job_family: Optional[str] = None
    # NEW: optional context chunks for RAG
    chunks: Optional[List[str]] = []

class JDUpdateRequest(BaseModel):
    jd_id: int
    content_md: str
    updated_by: Optional[str] = None

class JDVersionResponse(BaseModel):
    version_number: int
    content_md: str
    edited_at: datetime
    edited_by: str
    change_summary: Optional[str] = None

class JDGenerateResponse(BaseModel):
    jd_id: int
    content_md: str
    version: int