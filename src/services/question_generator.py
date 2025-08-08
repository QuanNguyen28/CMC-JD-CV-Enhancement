# src/services/question_generator.py
from typing import List, Dict, Any
from src.services.llm_prompt_orchestrator import generate_jd_text

class QuestionGenerator:
    @staticmethod
    def generate_questions(jd_id: int, types: List[str]) -> List[Dict[str, Any]]:
        """
        Generate interview questions for a JD by types: technical, behavioral, etc.
        """
        # Fetch JD content from DB or versioning service if needed
        from src.crud.jd_crud import get_jd_content
        raw_content = get_jd_content(jd_id)
        questions = []
        for qtype in types:
            metadata = {"raw_text": raw_content, "question_type": qtype}
            content, _ = generate_jd_text(metadata)
            questions.append({"type": qtype, "question": content})
        return questions
