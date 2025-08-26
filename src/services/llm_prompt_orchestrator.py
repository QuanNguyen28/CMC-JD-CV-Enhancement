# src/services/llm_prompt_orchestrator.py
"""
Builds and calls the LLM (Gemini) for JD generation & improvement, with optional RAG chunks.
"""
import os
import time
from typing import Tuple, Dict, Any, List, Generator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from google import genai

from src.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL
from src.services.jd_versioning_service import record_jd_version

# Initialize GenAI client (google-genai SDK)
_client = genai.Client(api_key=GEMINI_API_KEY)

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

def _render_prompt(context: Dict[str, Any]) -> str:
    """
    Render prompt from template if available; otherwise, fallback inline.
    """
    try:
        tmpl = env.get_template("jd_generation.j2")
        # pass context keys directly (template should expect title/level/department/job_family/chunks_text)
        return tmpl.render(**context)
    except Exception:
        # Fallback: inline prompt with optional chunks_text
        title = context.get("title", "")
        department = context.get("department", "")
        level = context.get("level", "")
        job_family = context.get("job_family", "")
        chunks_text = context.get("chunks_text", "")

        sections: List[str] = [
            "You are an expert HR assistant. Draft a high-quality Job Description in Markdown.",
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
            """
Return Markdown with sections:
- Summary
- Responsibilities (bullet points)
- Requirements (must-have vs. nice-to-have)
- Skills (technical & soft)
- Benefits / Working conditions
- Interview focus (bullet points)
            """.strip()
        )
        return "\n\n".join(sections)

def _llm_generate(prompt: str) -> str:
    """
    Call Gemini and return plain text/markdown via models.generate_content.
    """
    resp = _client.models.generate_content(
        model=GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    text = getattr(resp, "text", "") or ""
    return text.strip() or "# Job Description\n\n(Empty content)"

def generate_jd_text(metadata: Dict[str, Any], db: Session) -> Tuple[str, int]:
    """
    Generate a job description via LLM and record the first version.
    Expects metadata to contain: jd_id, created_by, title/department/level/job_family,
    and optional chunks_text.
    """
    prompt = _render_prompt(metadata)
    content_md = _llm_generate(prompt)

    version = record_jd_version(
        db,
        jd_id=metadata.get("jd_id"),
        content_md=content_md,
        updated_by=metadata.get("created_by") or "system",
        change_summary="initial generate with optional RAG chunks",
    )
    return content_md, version

# Live suggestion / Improve helpers 
def improve_jd(content_md: str, instruction: str = "", language: str = "vi") -> str:
    """
    Cải thiện toàn văn JD theo instruction.
    """
    sys = "You are an expert HR/Recruiting writer. Keep Markdown, keep factual info."
    lang_hint = "Vietnamese" if language == "vi" else "English"
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
    Gợi ý bullets/đoạn cho một section cụ thể, có thể tận dụng chunks_text (RAG).
    """
    sys = "You are an expert HR/Recruiting writer. Keep Markdown bullets concise."
    lang_hint = "Vietnamese" if language == "vi" else "English"
    sec = section or "Responsibilities"
    g = goal or "Suggest 5-8 concise bullets aligned with the tone."

    ctx = f"\n\n### Context (chunks)\n{chunks_text}\n" if chunks_text else ""

    prompt = f"""{sys}
Language: {lang_hint}

Goal: {g}
Target section: {sec}
Return only a Markdown list (no intro text){',' if language=='en' else ''} each bullet ≤ 22 words.

--- Current JD (Markdown) ---
{content_md}
{ctx}
"""
    text = _llm_generate(prompt)
    # Chuẩn hoá ra list bullets
    lines = [ln.strip("-• ").strip() for ln in text.splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln and not ln.lower().startswith("#")]
    return {"bullets": bullets[:12], "rationale": None}

def fake_streaming(text: str, delay_sec: float = 0.05) -> Generator[str, None, None]:
    """
    Giả streaming SSE bằng cách cắt nhỏ text thành câu/đoạn và yield dần.
    """
    parts = [p for p in text.split("\n") if p is not None]
    for p in parts:
        yield f"data: {p}\n\n"
        time.sleep(delay_sec)

    lang_hint = "Vietnamese" if language == "vi" else "English"
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
    Gợi ý bullets/đoạn cho một section cụ thể, có thể tận dụng chunks_text (RAG).
    """
    sys = "You are an expert HR/Recruiting writer. Keep Markdown bullets concise."
    lang_hint = "Vietnamese" if language == "vi" else "English"
    sec = section or "Responsibilities"
    g = goal or "Suggest 5-8 concise bullets aligned with the tone."

    ctx = f"\n\n### Context (chunks)\n{chunks_text}\n" if chunks_text else ""

    prompt = f"""{sys}
Language: {lang_hint}

Goal: {g}
Target section: {sec}
Return only a Markdown list (no intro text){',' if language=='en' else ''} each bullet ≤ 22 words.

--- Current JD (Markdown) ---
{content_md}
{ctx}
"""
    text = _llm_generate(prompt)
    # Chuẩn hoá ra list bullets
    lines = [ln.strip("-• ").strip() for ln in text.splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln and not ln.lower().startswith("#")]
    return {"bullets": bullets[:12], "rationale": None}

def fake_streaming(text: str, delay_sec: float = 0.05) -> Generator[str, None, None]:
    """
    Giả streaming SSE bằng cách cắt nhỏ text thành câu/đoạn và yield dần.
    """
    parts = [p for p in text.split("\n") if p is not None]
    for p in parts:
        yield f"data: {p}\n\n"
        time.sleep(delay_sec)