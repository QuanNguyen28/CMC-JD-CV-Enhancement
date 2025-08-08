from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JDGenerateRequest(BaseModel):
    title: str
    department: str
    level: str
    job_family: str

class JDUpdateRequest(BaseModel):
    jd_id: int
    content_md: str
    change_summary: Optional[str] = None  # tuỳ chọn

class JDVersionResponse(BaseModel):
    version_number: int
    content_md: str
    edited_at: datetime
    edited_by: str

class JDGenerateResponse(BaseModel):
    jd_id: int
    content_md: str
    version: int  # sẽ trả về version_number hiện tại