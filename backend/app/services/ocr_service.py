"""Text extraction: pypdf primary, pdfplumber fallback for PDFs; plain .txt
files are read directly (used by the demo sample docs). Neither library does
true OCR on scanned/image-only pages - this build follows the documented
"OCR: pypdf -> pdfplumber fallback" design, not a Tesseract/PaddleOCR path."""
import logging
import os

import pdfplumber
from pypdf import PdfReader

logger = logging.getLogger(__name__)

MIN_CHARS_PER_PAGE = 20


def _extract_with_pypdf(file_path: str) -> tuple[str, int]:
    reader = PdfReader(file_path)
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(texts), len(reader.pages)


def _extract_with_pdfplumber(file_path: str) -> tuple[str, int]:
    with pdfplumber.open(file_path) as pdf:
        texts = [page.extract_text() or "" for page in pdf.pages]
        return "\n\n".join(texts), len(pdf.pages)


def extract_text(file_path: str) -> tuple[str, float]:
    """Returns (text, ocr_quality in [0,1])."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return text, 1.0

    text, page_count = _extract_with_pypdf(file_path)
    if page_count and len(text) / page_count >= MIN_CHARS_PER_PAGE:
        return text, 0.95

    try:
        fallback_text, fallback_pages = _extract_with_pdfplumber(file_path)
        if len(fallback_text) > len(text):
            quality = 0.75 if fallback_pages and len(fallback_text) / fallback_pages >= MIN_CHARS_PER_PAGE else 0.4
            return fallback_text, quality
    except Exception as exc:  # noqa: BLE001
        logger.warning("pdfplumber fallback failed: %s", exc)

    return text, 0.3 if text.strip() else 0.0
