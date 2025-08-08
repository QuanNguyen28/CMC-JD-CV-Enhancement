# src/utils/file_extract.py
"""
Utilities to extract raw text from various file formats:
- PDF
- DOCX
- Plain text
- Images (OCR via pytesseract)
"""
import io
from typing import Union

from PyPDF2 import PdfReader
from docx import Document
from PIL import Image, ImageSequence, ImageOps
import pytesseract


def extract_text_from_pdf(data: bytes) -> str:
    """
    Extract text from PDF bytes using PyPDF2.
    Returns "" on failure.
    """
    try:
        with io.BytesIO(data) as pdf_io:
            reader = PdfReader(pdf_io)
            texts = []
            for page in reader.pages:
                try:
                    t = page.extract_text() or ""
                except Exception:
                    t = ""
                texts.append(t)
            return "\n".join(texts).strip()
    except Exception:
        return ""


def extract_text_from_docx(data: bytes) -> str:
    """
    Extract text from DOCX bytes.
    Returns "" on failure.
    """
    try:
        with io.BytesIO(data) as docx_io:
            doc = Document(docx_io)
            return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception:
        return ""


def _ocr_image(img: Image.Image) -> str:
    """
    OCR a single PIL Image with basic pre-processing.
    """
    try:
        # Correct orientation via EXIF and ensure RGB
        img = ImageOps.exif_transpose(img).convert("RGB")
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""


def extract_text_from_image(data: bytes) -> str:
    """
    Perform OCR on image bytes (supports multi-frame images like TIFF).
    Returns "" on failure.
    """
    try:
        with io.BytesIO(data) as img_io:
            with Image.open(img_io) as im:
                texts = []
                # Iterate frames if available (e.g., TIFF)
                for frame in ImageSequence.Iterator(im):
                    txt = _ocr_image(frame)
                    if txt:
                        texts.append(txt)
                # Fallback: if no frames captured text, try the original
                if not texts:
                    texts.append(_ocr_image(im))
                return "\n".join(filter(None, texts)).strip()
    except Exception:
        return ""


def extract_text_from_file(data: bytes, filename: str) -> str:
    """
    Route to the correct extractor based on file extension.
    Falls back to UTF-8 decode on unknown/unsupported types.
    """
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()

    if ext == "pdf":
        return extract_text_from_pdf(data)

    # NOTE: python-docx does NOT support legacy .doc; treat .doc as plain text fallback.
    if ext == "docx":
        return extract_text_from_docx(data)

    if ext in ("png", "jpg", "jpeg", "tif", "tiff", "bmp", "gif", "webp"):
        return extract_text_from_image(data)

    # fallback assume plain text
    try:
        return data.decode("utf-8")
    except Exception:
        return ""