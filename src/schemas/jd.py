# src/schemas/jd.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JDGenerateRequest(BaseModel):
    title: str
    department: Optional[str] = None
    level: Optional[str] = None
    job_family: Optional[str] = None
    language: str = "vi"
    chunks_text: Optional[str] = None

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

class JDSuggestRequest(BaseModel):
    content_md: str
    section: Optional[str] = "Responsibilities"
    goal: Optional[str] = ""
    language: str = "vi"
    chunks_text: Optional[str] = ""

class JDImproveRequest(BaseModel):
    content_md: str
    instruction: Optional[str] = (
        "Improve clarity, structure, and tone; keep Markdown; preserve facts."
    )
    language: str = "vi"
    create_new_version: bool = False 

class JDImproveResponse(BaseModel):
    content_md: str
    version: Optional[int] = None

class JDSuggestResponse(BaseModel):
    suggestions: List[str]
    rationale: Optional[str] = None