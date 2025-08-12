# src/services/question_generator.py (advanced refactor)
# NOTE: Backwards-compatible: keep public generate_questions(...) signature
# Enhancements:
# - Strong typing via TypedDict & dataclasses
# - Deterministic seeding via SHA-256 over context
# - Robust JSON extraction (fenced + balanced braces) & tolerant cleanup
# - MMR-like diversification using character n-gram Jaccard
# - Coverage constraints across types & focuses
# - Provider Strategy pattern (LLM providers pluggable)
# - Jinja2 template manager with custom filters + graceful fallback
# - Safety filters (very light-weight) & question normalization
# - Rich metadata return (internally) while exposing same public list[dict]
# - Minimal deps: stdlib + jinja2 only

from __future__ import annotations

import os
import re
import json
import time
import math
import hashlib
import random
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterable, Tuple, TypedDict

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

# ============================================================================
# Logging (JSON-ish)
# ============================================================================
_logger = logging.getLogger("question_generator")
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    _handler.setFormatter(_fmt)
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)

# ============================================================================
# Types & Models
# ============================================================================
class QuestionDict(TypedDict, total=False):
    type: str
    question: str
    competency: str
    difficulty: str
    rubric: str

@dataclass
class GenerationContext:
    jd_markdown: str
    title: str
    level: str
    department: str
    focus: List[str]
    count: int
    mix: List[str]  # e.g., ["technical","behavioral","situational"]
    language: str = "vi"

@dataclass
class Question:
    type: str
    question: str
    competency: str
    difficulty: str
    rubric: str

@dataclass
class GenMeta:
    provider: str
    seed: int
    elapsed_ms: int
    dedup_ratio: float
    coverage: Dict[str, int]

@dataclass
class GenResult:
    questions: List[Question]
    meta: GenMeta

# ============================================================================
# ENV helpers
# ============================================================================

def _env_flag(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1","true","t","yes","y","on"}

LLM_BYPASS: bool = _env_flag("LLM_BYPASS", True)
LLM_PROVIDER: str = (os.getenv("LLM_PROVIDER") or "").strip().lower()

try:
    # optional; do not fail if missing
    from src.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL, OPENAI_API_KEY, OPENAI_MODEL
except Exception:  # pragma: no cover
    GEMINI_API_KEY = None
    GEMINI_CHAT_MODEL = None
    OPENAI_API_KEY = None
    OPENAI_MODEL = None

# ============================================================================
# Template manager with filters
# ============================================================================
TEMPLATE_DIR = (Path(__file__).resolve().parents[1] / "api" / "v1" / "templates")

def _filter_truncate(s: str, n: int = 200) -> str:
    s = str(s)
    return s if len(s) <= n else s[: max(0, n - 1)] + "…"

def _filter_stripmd(s: str) -> str:
    # naive markdown strip
    return re.sub(r"[#*_>`]+", "", s or "").strip()

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["j2"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["truncate"] = _filter_truncate
_env.filters["stripmd"] = _filter_stripmd


def _render_prompt(ctx: GenerationContext) -> str:
    try:
        tmpl = _env.get_template("interview_questions.j2")
        return tmpl.render(**asdict(ctx))
    except TemplateNotFound:
        _logger.warning("Template 'interview_questions.j2' not found. Using fallback prompt.")
        return (
            "Generate interview questions as JSON with key 'questions'.\n"
            f"Role: {ctx.title} | Level: {ctx.level} | Department: {ctx.department} | Language: {ctx.language}\n"
            f"Focus: {', '.join(ctx.focus)} | Types: {', '.join(ctx.mix)} | Count: {ctx.count}\n"
        )

# ============================================================================
# JSON extraction / cleanup
# ============================================================================
_FENCED_JSON_RE = re.compile(r"```json\s*(\{[\s\S]+?\})\s*```", re.IGNORECASE)
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _extract_json_block(s: str) -> Optional[str]:
    # 1) fenced
    m = _FENCED_JSON_RE.search(s)
    if m:
        return m.group(1)
    # 2) balanced braces (stack)
    starts = [i for i, ch in enumerate(s) if ch == "{"]
    for start in starts:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(s)):
            ch = s[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        chunk = s[start : i + 1]
                        try:
                            json.loads(chunk)
                            return chunk
                        except Exception:
                            # try tolerant cleanup (remove trailing commas)
                            cleaned = _TRAILING_COMMA_RE.sub(r"\\1", chunk)
                            try:
                                json.loads(cleaned)
                                return cleaned
                            except Exception:
                                break
    return None


# ============================================================================
# Similarity & diversification
# ============================================================================

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _char_ngrams(s: str, n: int = 4) -> set:
    s = _normalize(s)
    if len(s) < n:
        return {s}
    return {s[i:i+n] for i in range(len(s)-n+1)}


def _jaccard(a: str, b: str, n: int = 4) -> float:
    A, B = _char_ngrams(a, n), _char_ngrams(b, n)
    if not A and not B:
        return 1.0
    return len(A & B) / max(1, len(A | B))


def _mmr_select(candidates: List[Question], k: int, lambda_div: float = 0.75) -> List[Question]:
    """MMR-like greedy selection over simple lexical similarity.
    score(item) = base_quality - lambda * max_sim_to_selected
    Here base_quality is approximated from heuristic signals (length, punctuation variety).
    """
    def base_quality(q: Question) -> float:
        txt = q.question
        L = len(txt)
        punct_bonus = sum(ch in "?!." for ch in txt)
        return min(1.0, (L / 120.0)) + 0.1 * punct_bonus

    selected: List[Question] = []
    remaining = candidates[:]
    while remaining and len(selected) < k:
        best_q, best_sc = None, -1e9
        for q in remaining:
            sim_penalty = 0.0
            if selected:
                sim_penalty = max(_jaccard(q.question, s.question) for s in selected)
            sc = base_quality(q) - lambda_div * sim_penalty
            if sc > best_sc:
                best_q, best_sc = q, sc
        selected.append(best_q)
        remaining.remove(best_q)
    return selected


# ============================================================================
# Safety filters (very light)
# ============================================================================
_PII_RE = re.compile(r"(\b\d{9,}\b|\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b)")


def _safety_scrub(s: str) -> str:
    # redacts very simple PII patterns (emails, long digit strings)
    return _PII_RE.sub("[REDACTED]", s or "")


# ============================================================================
# Offline generator (bypass mode)
# ============================================================================
_TEMPLATES: Dict[str, List[str]] = {
    "technical": [
        "Thiết kế giải pháp cho {focus} trong bối cảnh {title} ({level}). Trade-off là gì?",
        "Bạn đo lường chất lượng/độ tin cậy cho {focus} như thế nào? Chỉ số chính?",
        "Khi {focus} cần mở rộng X10, bạn xử lý nút thắt cổ chai ra sao?",
        "Nếu {focus} gặp sự cố production, quy trình RCA và ngăn tái diễn?",
        "Vì sao chọn công nghệ/kiến trúc cho {focus} thay vì phương án khác?",
    ],
    "behavioral": [
        "Kể lần bạn thuyết phục team đổi giải pháp. Cách tiếp cận và kết quả?",
        "Bạn xử lý xung đột ưu tiên như thế nào khi deadline gắt?",
        "Bạn nhận phản hồi khó nghe ở code review—bạn phản hồi và cải thiện ra sao?",
        "Bạn giúp đồng đội mới hiểu nhanh bối cảnh dự án như thế nào?",
        "Bạn cân bằng giữa tốc độ và chất lượng ra sao?",
    ],
    "situational": [
        "Giả sử hệ thống tăng latency bất thường. Bạn chẩn đoán và xử lý thế nào?",
        "Yêu cầu thay đổi gấp, rủi ro cao. Lộ trình giảm rủi ro của bạn?",
        "Có lỗ hổng bảo mật liên quan {focus}. Các bước phối hợp fix?",
        "Pipeline build flakey khiến CI đỏ ngẫu nhiên. Bạn khắc phục ra sao?",
        "Khi yêu cầu mơ hồ, bạn khai phá và chốt phạm vi như thế nào?",
    ],
}


def _stable_seed(*parts: str) -> int:
    s = "|".join(p or "" for p in parts)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)  # 32-bit seed


def _expand_focus(focus: List[str]) -> List[str]:
    # very small synonym-style expansion (extensible)
    MAP = {
        "system design": ["kiến trúc", "scalability", "availability"],
        "python": ["asyncio", "typing", "performance"],
        "data": ["etl", "quality", "governance"],
    }
    out = list(focus)
    for f in focus or ["system design"]:
        out.extend(MAP.get(f.lower(), []))
    # unique, preserve order
    seen = set()
    uniq = []
    for x in out:
        xl = x.lower()
        if xl not in seen:
            seen.add(xl)
            uniq.append(x)
    return uniq


def _offline_generate(ctx: GenerationContext, seed: int) -> GenResult:
    rng = random.Random(seed)
    focuses = _expand_focus(ctx.focus)

    # Candidate pool with coverage across types & focuses
    cands: List[Question] = []
    for i in range(max(1, ctx.count * 3)):
        t = ctx.mix[i % len(ctx.mix)]
        tpl = rng.choice(_TEMPLATES.get(t, _TEMPLATES["technical"]))
        f = focuses[i % len(focuses)] if focuses else "system design"
        q = tpl.format(title=ctx.title, level=ctx.level, department=ctx.department, focus=f)
        q = _safety_scrub(q)
        cands.append(Question(
            type=t,
            question=q,
            competency=(f if t == "technical" else ("communication" if t == "behavioral" else "problem solving")),
            difficulty=ctx.level.lower(),
            rubric="Câu trả lời nên có cấu trúc (STAR/kỹ thuật), nêu trade-off và kết quả.",
        ))

    # Diversify with MMR-like selection
    selected = _mmr_select(cands, ctx.count)

    # Dedup metric
    uniq = { _normalize(q.question) for q in selected }
    dedup_ratio = 1.0 - (len(uniq) / max(1, len(selected)))

    # Coverage stats
    cov: Dict[str, int] = {}
    for q in selected:
        cov[q.type] = cov.get(q.type, 0) + 1

    meta = GenMeta(provider="bypass", seed=seed, elapsed_ms=0, dedup_ratio=dedup_ratio, coverage=cov)
    return GenResult(questions=selected, meta=meta)


# ============================================================================
# Providers (Strategy)
# ============================================================================
class Provider:
    name: str = "base"

    def generate(self, prompt: str, ctx: GenerationContext) -> str:
        raise NotImplementedError


class GeminiProvider(Provider):
    name = "gemini"

    def generate(self, prompt: str, ctx: GenerationContext) -> str:
        # Placeholder; raise to force explicit implementation in your repo
        raise RuntimeError("Gemini provider not implemented. Set LLM_BYPASS=1 or implement SDK call.")


class OpenAIProvider(Provider):
    name = "openai"

    def generate(self, prompt: str, ctx: GenerationContext) -> str:
        raise RuntimeError("OpenAI provider not implemented. Set LLM_BYPASS=1 or implement SDK call.")


def _get_provider() -> Provider:
    if LLM_PROVIDER == "gemini":
        return GeminiProvider()
    if LLM_PROVIDER == "openai":
        return OpenAIProvider()
    return Provider()  # will raise if used


# ============================================================================
# LLM parsing & normalization
# ============================================================================

def _parse_questions_from_text(text: str) -> List[Question]:
    # 1) direct JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("questions"), list):
            return [ _coerce_question(d) for d in data["questions"] ]
    except Exception:
        pass

    # 2) fenced or balanced braces
    block = _extract_json_block(text)
    if block:
        try:
            data = json.loads(block)
            if isinstance(data, dict) and isinstance(data.get("questions"), list):
                return [ _coerce_question(d) for d in data["questions"] ]
        except Exception:
            pass

    # 3) fallback: bullets/lines
    out: List[Question] = []
    for line in text.splitlines():
        line = line.strip(" -*\t")
        if len(line) >= 5:
            out.append(Question(
                type="mixed",
                question=_safety_scrub(line),
                competency="",
                difficulty="",
                rubric="",
            ))
            if len(out) >= 8:
                break
    return out


def _coerce_question(d: Dict[str, Any]) -> Question:
    return Question(
        type=str(d.get("type") or "mixed"),
        question=_safety_scrub(str(d.get("question") or "")),
        competency=str(d.get("competency") or ""),
        difficulty=str(d.get("difficulty") or ""),
        rubric=str(d.get("rubric") or ""),
    )


# ============================================================================
# Public API (backwards-compatible)
# ============================================================================

def generate_questions(
    jd_markdown: Optional[str],
    title: Optional[str],
    level: Optional[str],
    department: Optional[str],
    focus: List[str],
    count: int,
    mix: List[str],
    language: str = "vi",
) -> List[Dict[str, Any]]:
    """
    Backwards-compatible facade: returns List[Dict[str, Any]].
    Internally uses advanced pipeline for offline or LLM mode.
    """
    ctx = GenerationContext(
        jd_markdown=jd_markdown or "",
        title=title or "Role",
        level=level or "Mid",
        department=department or "General",
        focus=focus or [],
        count=int(count or 8),
        mix=(mix or ["technical", "behavioral", "situational"]),
        language=language or "vi",
    )

    seed = _stable_seed(ctx.title, ctx.level, ctx.department, ",".join(ctx.focus), ",".join(ctx.mix), ctx.language)

    t0 = time.time()
    if LLM_BYPASS:
        result = _offline_generate(ctx, seed)
    else:
        prompt = _render_prompt(ctx)
        provider = _get_provider()
        if isinstance(provider, Provider) and provider.name == "base":
            raise RuntimeError(
                "LLM_PROVIDER is not set or unsupported. Use LLM_BYPASS=1 or set LLM_PROVIDER=gemini|openai."
            )
        raw = provider.generate(prompt, ctx)
        qs = _parse_questions_from_text(raw)
        # diversification on LLM output as well
        qs = _mmr_select(qs, ctx.count)
        cov: Dict[str, int] = {}
        for q in qs:
            cov[q.type] = cov.get(q.type, 0) + 1
        uniq = { _normalize(q.question) for q in qs }
        result = GenResult(
            questions=qs,
            meta=GenMeta(provider=provider.name, seed=seed, elapsed_ms=0, dedup_ratio=1.0 - len(uniq)/max(1,len(qs)), coverage=cov),
        )

    elapsed = int((time.time() - t0) * 1000)
    result.meta.elapsed_ms = elapsed

    # Emit a concise log (safe)
    _logger.info(
        "generated_questions", extra={
            "provider": result.meta.provider,
            "count": len(result.questions),
            "coverage": result.meta.coverage,
            "dedup_ratio": round(result.meta.dedup_ratio, 3),
            "elapsed_ms": result.meta.elapsed_ms,
        }
    )

    # Convert to public List[Dict]
    return [
        {
            "type": q.type,
            "question": q.question,
            "competency": q.competency,
            "difficulty": q.difficulty,
            "rubric": q.rubric,
        }
        for q in result.questions
    ]
