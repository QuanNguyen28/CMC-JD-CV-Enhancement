# src/schemas/interview.py
from pydantic import BaseModel
from typing import List

class InterviewRequest(BaseModel):
    jd_id: int
    types: List[str]

class Question(BaseModel):
    type: str
    question: str

class InterviewResponse(BaseModel):
    jd_id: int
    questions: List[Question]