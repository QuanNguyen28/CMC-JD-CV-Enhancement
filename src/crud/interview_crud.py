# src/crud/interview_crud.py
"""
Interview CRUD: no-op, since we no longer persist questions.
"""
def save_interview_questions(db, jd_id, questions):
    # persistence removed; questions are returned directly to client
    return questions