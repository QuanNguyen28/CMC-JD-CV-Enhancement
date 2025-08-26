# src/schemas/jd_live.py
from typing import List, Optional, Literal
from pydantic import BaseModel

class JDImproveRequest(BaseModel):
    content_md: str
    instruction: Optional[str] = (
        "Improve clarity, structure, and tone; keep Markdown; preserve facts."
    )
    language: Optional[Literal["vi", "en"]] = "vi"
    create_new_version: bool = False  # nếu true thì lưu lại version mới

class JDImproveResponse(BaseModel):
    content_md: str
    version: Optional[int] = None

class JDSuggestRequest(BaseModel):
    content_md: str
    section: Optional[str] = None  # ví dụ: "Summary", "Responsibilities", "Requirements"
    goal: Optional[str] = (
        "Suggest 5-8 concise bullets aligned with the tone. Keep Markdown."
    )
    language: Optional[Literal["vi", "en"]] = "vi"
    # Nếu bạn đã có text từ RAG chunks, đưa vào đây
    chunks_text: Optional[str] = None

class JDSuggestResponse(BaseModel):
    suggestions: List[str]
    rationale: Optional[str] = None