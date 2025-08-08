# src/api/v1/interview.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.interview import InterviewRequest, InterviewResponse, Question
from src.services.question_generator import QuestionGenerator
from src.api.dependencies import require_roles

router = APIRouter(prefix="/v1/interview", tags=["Interview"])

@router.post("/generate", response_model=InterviewResponse)
def generate_interview(
    req: InterviewRequest,
    current_user=Depends(require_roles("recruiter", "admin"))
):
    """
    Generate interview questions on the fly and return them (no DB persistence).
    """
    try:
        questions = QuestionGenerator.generate_questions(req.jd_id, req.types)
        # Return as InterviewResponse without saving
        return InterviewResponse(jd_id=req.jd_id, questions=[
            Question(type=q["type"], question=q["question"]) for q in questions
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))