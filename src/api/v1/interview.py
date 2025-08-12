# src/api/v1/interview.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, require_roles
from src.db.models import JobDescription
from src.services.question_generator import generate_questions

router = APIRouter(prefix="/v1/interview", tags=["Interview"])

class InterviewReq(BaseModel):
    jd_id: Optional[int] = None
    title: Optional[str] = None
    level: Optional[str] = None
    department: Optional[str] = None
    focus: Optional[List[str]] = []
    count: Optional[int] = 8
    mix: Optional[List[str]] = ["technical", "behavioral", "situational"]
    language: Optional[str] = "vi"

class InterviewRespItem(BaseModel):
    type: str
    question: str
    competency: str
    difficulty: str
    rubric: Optional[str] = None

class InterviewResp(BaseModel):
    questions: List[InterviewRespItem]

@router.post("/generate", response_model=InterviewResp)
def generate_interview_endpoint(
    req: InterviewReq,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("recruiter", "admin")),
):
    try:
        jd_md = None
        if req.jd_id:
            jd = db.query(JobDescription).filter(JobDescription.jd_id == req.jd_id).first()
            if not jd:
                raise HTTPException(status_code=404, detail="JD not found")
            jd_md = jd.content_md
            # fallback điền thiếu
            req.title = req.title or jd.title
            req.level = req.level or jd.level
            req.department = req.department or jd.department

        qs = generate_questions(
            jd_markdown=jd_md,
            title=req.title,
            level=req.level,
            department=req.department,
            focus=req.focus or [],
            count=req.count or 8,
            mix=req.mix or ["technical", "behavioral", "situational"],
            language=req.language or "vi",
        )
        return {"questions": qs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview generation failed: {e}")