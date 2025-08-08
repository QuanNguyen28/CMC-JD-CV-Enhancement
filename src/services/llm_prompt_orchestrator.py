# src/services/llm_prompt_orchestrator.py
"""
Builds and calls the LLM (Gemini) for JD generation & improvement using the Google Gen AI SDK.
"""
import os
from typing import Tuple, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from google import genai
from pytest import Session

from src import db
from src.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL
from src.services.jd_versioning_service import record_jd_version

# Initialize GenAI client
client = genai.Client(api_key=GEMINI_API_KEY)

# Jinja2 environment setup
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../api/v1/templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["j2"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

def generate_jd_text(metadata: Dict[str, str], db: Session) -> Tuple[str, int]:
    """
    Generate a job description markdown via LLM and record version.
    Returns: (content_md, version)
    """
    tmpl = env.get_template("jd_generation.j2")
    prompt = tmpl.render(metadata=metadata)
    # Start chat session
    chat = client.chats.create(model=GEMINI_CHAT_MODEL)
    # System instruction + user prompt
    system_msg = "You are an expert at crafting job descriptions."
    response = chat.send_message(f"{system_msg}\n{prompt}")
    content_md = response.text
    version = record_jd_version(db, content_md, metadata)
    return content_md, version

def improve_jd_text(raw_text: str) -> str:
    """
    Enhance an existing JD for clarity and completeness.
    """
    tmpl = env.get_template("jd_improvement.j2")
    prompt = tmpl.render(raw=raw_text)
    chat = client.chats.create(model=GEMINI_CHAT_MODEL)
    system_msg = "Enhance this job description for clarity and completeness."
    response = chat.send_message(f"{system_msg}\n{prompt}")
    return response.text