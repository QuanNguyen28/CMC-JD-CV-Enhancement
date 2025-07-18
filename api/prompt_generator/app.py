#!/usr/bin/env python
"""
api/prompt_generator/app.py

FastAPI service for:
 - Generating Job Descriptions   (/generate_jd)
 - Generating Interview Questions (/generate_questions)
 - Improving an existing JD file  (/improve_jd)

All AI calls use Gemini REST API with API key.
"""

import os
import io
import glob
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import requests
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
from PIL import Image
import pytesseract

# load .env
load_dotenv()

API_KEY        = os.getenv("GEMINI_API_KEY")
CHAT_MODEL     = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
EMBED_MODEL    = os.getenv("GEMINI_EMBED_MODEL", "embed-gecko-001")

CHAT_ENDPOINT  = f"https://gemini.api.cloud.google.com/v1/models/{CHAT_MODEL}:generateMessage"
EMBED_ENDPOINT = f"https://gemini.api.cloud.google.com/v1/models/{EMBED_MODEL}:embedText"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set in .env")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Jinja2 setup
HERE       = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, "templates")
env        = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

app = FastAPI(title="Prompt Generator (Gemini API)")

class RequestModel(BaseModel):
    title: str
    level: str
    department: str
    chunks: list[str]

class JDResponse(BaseModel):
    job_description: str

class QuestionsResponse(BaseModel):
    interview_questions: str

def call_gemini_chat(system: str, user: str, temperature: float):
    payload = {
        "model": CHAT_MODEL,
        "temperature": temperature,
        "candidateCount": 1,
        "promptMessages": [
            {"author": "system", "content": system},
            {"author": "user",   "content": user}
        ]
    }
    resp = requests.post(CHAT_ENDPOINT, json=payload, headers=HEADERS, timeout=60)
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json()
    return data["candidates"][0]["content"].strip()

def extract_text_from_file(contents: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_pdf(io.BytesIO(contents))
    if ext == "docx":
        doc = Document(io.BytesIO(contents))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext in ("jpg", "jpeg", "png"):
        return pytesseract.image_to_string(Image.open(io.BytesIO(contents)))
    raise HTTPException(status_code=400, detail="Unsupported file type")

@app.post("/generate_jd", response_model=JDResponse)
def generate_jd(req: RequestModel):
    tpl = env.get_template("jd_generation.j2")
    user_prompt = tpl.render(metadata=req.dict(), chunks=req.chunks)
    system_msg = "You are a helpful assistant that crafts clear, concise job descriptions."
    jd = call_gemini_chat(system_msg, user_prompt, temperature=0.3)
    return JDResponse(job_description=jd)

@app.post("/generate_questions", response_model=QuestionsResponse)
def generate_questions(req: RequestModel):
    tpl = env.get_template("interview_questions.j2")
    user_prompt = tpl.render(metadata=req.dict(), chunks=req.chunks)
    system_msg = "You are an expert interviewer who produces behavioral and technical questions."
    qs = call_gemini_chat(system_msg, user_prompt, temperature=0.4)
    return QuestionsResponse(interview_questions=qs)

@app.post("/improve_jd")
async def improve_jd(file: UploadFile = File(...)):
    contents = await file.read()
    text = extract_text_from_file(contents, file.filename)
    # simple chunk: pass full text as one prompt
    tpl = env.get_template("jd_improvement.j2")
    prompt = tpl.render(raw=text)
    system_msg = "You are an AI assistant that improves and enhances job descriptions."
    improved = call_gemini_chat(system_msg, prompt, temperature=0.3)
    return {"improved_jd": improved}

@app.get("/ping")
def ping():
    return {"pong": True}
