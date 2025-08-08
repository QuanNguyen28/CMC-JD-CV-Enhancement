# src/main.py

import uvicorn
from fastapi import FastAPI

from src.api.auth.auth import router as auth_router
from src.api.v1.jd import router as jd_router
from src.api.v1.interview import router as interview_router
from src.api.v1.roles import router as roles_router
from src.api.v1.retriever import router as retrieve_router

app = FastAPI(
    title="SmartHire Composer API",
    version="1.0.0",
    description="AI-powered assistant for creating and managing job descriptions & interview questions"
)

# Authentication (no extra prefix)
app.include_router(auth_router)

# Versioned v1 endpoints, will live under /v1
app.include_router(jd_router, prefix="")
app.include_router(interview_router, prefix="")
app.include_router(roles_router, prefix="")

# Retriever (semantic search)
app.include_router(retrieve_router, prefix="")

@app.get("/ping", tags=["health"])
def ping():
    return {"pong": True}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)