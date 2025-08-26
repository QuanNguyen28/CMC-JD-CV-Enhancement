# src/services/llm_prompt_orchestrator.py
"""
Builds and calls the LLM (Gemini) for JD generation & improvement, with optional RAG chunks.
- Fixes duplicated functions and stray code
- Adds explicit language control (vi/en)
- Imports request/response schemas for typing
"""
from __future__ import annotations

import os
import time
from typing import Tuple, Dict, Any, List, Generator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

# Schemas
from src.schemas.jd import (
    JDGenerateRequest,
    JDImproveRequest,      
    JDSuggestRequest,      
)

# Gemini (google-genai)
from google import genai
from src.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL
from src.services.jd_versioning_service import record_jd_version

# Initialize GenAI client (safe)
_client: genai.Client | None = None
if GEMINI_API_KEY:
    try:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        _client = None

# Jinja2 environment setup (point to /src/api/v1/templates)
TEMPLATE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "api", "v1", "templates")
)
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["j2"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

# -------------------------
# Prompt rendering helpers
# -------------------------

def _render_prompt(context: Dict[str, Any], language: str = "vi") -> str:
    """Render prompt from template if available; otherwise, fallback inline."""
    lang_hint = "Vietnamese" if (language or "vi").lower().startswith("vi") else "English"
    ctx = dict(context)
    ctx["language_hint"] = lang_hint
    try:
        tmpl = env.get_template("jd_generation.j2")
        # Template can use: title/level/department/job_family/chunks_text/language_hint
        return tmpl.render(**ctx)
    except Exception:
        # Fallback inline prompt
        title       = context.get("title", "")
        department  = context.get("department", "")
        level       = context.get("level", "")
        job_family  = context.get("job_family", "")
        chunks_text = context.get("chunks_text", "")

        sections: List[str] = [
            "You are an expert HR assistant. Draft a high-quality Job Description in Markdown.",
            f"Language: {lang_hint}",
            f"Role title: {title}",
        ]
        if department:
            sections.append(f"Department: {department}")
        if level:
            sections.append(f"Seniority level: {level}")
        if job_family:
            sections.append(f"Job family: {job_family}")
        if chunks_text:
            sections.append("### Context from chunks (internal, prioritize alignment):\n" + chunks_text)

        sections.append(
            (
                "Return Markdown with sections:\n"
                "- Summary\n"
                "- Responsibilities (bullet points)\n"
                "- Requirements (must-have vs. nice-to-have)\n"
                "- Skills (technical & soft)\n"
                "- Benefits / Working conditions\n"
                "- Interview focus (bullet points)"
            ).strip()
        )
        return "\n\n".join(sections)


def _llm_generate(prompt: str) -> str:
    """Call Gemini and return plain text/markdown via models.generate_content."""
    if _client is None:
        # Fail-soft: return prompt tail to avoid crashing in dev when quota/key missing
        return ("# Job Description\n\n" + prompt[:2000]).strip()
    resp = _client.models.generate_content(model=GEMINI_CHAT_MODEL, contents=prompt)
    text = getattr(resp, "text", "") or ""
    return text.strip() or "# Job Description\n\n(Empty content)"


# ------------------------------------
# Public functions used by API layer
# ------------------------------------

def generate_jd_text(metadata: Dict[str, Any], db: Session, lang: str = "vi") -> Tuple[str, int]:
    """
    Generate a job description via LLM and record the first version.
    Expects metadata to contain: jd_id, created_by, title/department/level/job_family,
    and optional chunks_text.
    """
    prompt = _render_prompt(metadata, language=lang)
    content_md = _llm_generate(prompt)

    version = record_jd_version(
        db,
        jd_id=metadata.get("jd_id"),
        content_md=content_md,
        updated_by=metadata.get("created_by") or "system",
        change_summary="initial generate with optional RAG chunks",
    )
    return content_md, version


def improve_jd(content_md: str, instruction: str = "", language: str = "vi") -> str:
    """Improve a full JD markdown according to instruction and language."""
    sys = "You are an expert HR/Recruiting writer. Keep Markdown and preserve factual information."
    lang_hint = "Vietnamese" if (language or "vi").lower().startswith("vi") else "English"
    inst = instruction or "Improve clarity, consistency, and tone; keep Markdown; preserve facts."

    prompt = f"""{sys}
Language: {lang_hint}

Instruction:
{inst}

--- Current JD (Markdown) ---
{content_md}
"""
    return _llm_generate(prompt)


def suggest_jd_section(
    content_md: str,
    section: str = "",
    goal: str = "",
    language: str = "vi",
    chunks_text: str = "",
) -> Dict[str, Any]:
    """
    Suggest bullets/paragraphs for a specific section, optionally using chunks_text (RAG context).
    Returns dict with list of bullets and optional rationale.
    """
    sys = "You are an expert HR/Recruiting writer. Keep Markdown bullets concise."
    lang_hint = "Vietnamese" if (language or "vi").lower().startswith("vi") else "English"
    sec = section or "Responsibilities"
    g = goal or "Suggest 5-8 concise bullets aligned with the tone."

    ctx = f"\n\n### Context (chunks)\n{chunks_text}\n" if chunks_text else ""

    prompt = f"""{sys}
Language: {lang_hint}

Goal: {g}
Target section: {sec}
Return only a Markdown list (no intro text){',' if lang_hint=='English' else ''} each bullet ≤ 22 words.

--- Current JD (Markdown) ---
{content_md}
{ctx}
"""
    text = _llm_generate(prompt)
    # Normalize to bullets
    lines = [ln.strip("-• ").strip() for ln in text.splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln and not ln.lower().startswith("#")]
    return {"bullets": bullets[:12], "rationale": None}


# -------------------------
# Streaming helper (fake)
# -------------------------

def fake_streaming(text: str, delay_sec: float = 0.05) -> Generator[str, None, None]:
    """Mock SSE streaming: yield the text line-by-line with small delays."""
    parts = [p for p in text.split("\n") if p is not None]
    for p in parts:
        yield f"data: {p}\n\n"
        time.sleep(delay_sec)