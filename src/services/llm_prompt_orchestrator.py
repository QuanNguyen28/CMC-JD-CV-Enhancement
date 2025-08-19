# src/services/llm_prompt_orchestrator.py
"""
Builds and calls the LLM (Gemini) for JD generation & improvement, with optional RAG chunks.
"""
import os
from typing import Tuple, Dict, Any, List
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
<<<<<<< HEAD
        # Pass context keys directly (template expects title/level/department/...)
        return tmpl.render(**context)
    except Exception:
        # Fallback: inline prompt with optional chunks_text
=======
        # pass context keys directly (template should expect title/level/department/job_family/chunks_text)
        return tmpl.render(**context)
    except Exception:
>>>>>>> 42eedfa (chore: merge with remote skeleton)
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
<<<<<<< HEAD
    Call Gemini and return plain text/markdown. Uses the responses API.
    """
    resp = _client.responses.generate(
        model=GEMINI_CHAT_MODEL,
        input=[{"role": "user", "content": prompt}],
    )
    # Collect text from candidates
    out: List[str] = []
    for cand in getattr(resp, "candidates", []) or []:
        content = getattr(cand, "content", None)
        if not content or not getattr(content, "parts", None):
            continue
        for part in content.parts:
            txt = getattr(part, "text", None)
            if txt:
                out.append(txt)
    text = "\n".join(out).strip()
    return text or "# Job Description\n\n(Empty content)"
=======
    Call Gemini and return plain text/markdown via models.generate_content.
    """
    resp = _client.models.generate_content(
        model=GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    text = getattr(resp, "text", "") or ""
    return text.strip() or "# Job Description\n\n(Empty content)"
>>>>>>> 42eedfa (chore: merge with remote skeleton)

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

def improve_jd_text(raw_text: str) -> str:
    """
    Enhance an existing JD for clarity and completeness.
    """
    try:
        tmpl = env.get_template("jd_improvement.j2")
        prompt = tmpl.render(raw=raw_text)
    except Exception:
        prompt = (
            "Enhance this job description for clarity and completeness. "
            "Return Markdown only.\n\n" + raw_text
        )
    return _llm_generate(prompt)