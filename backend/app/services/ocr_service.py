"""Text extraction: pypdf primary, pdfplumber fallback for PDFs; plain .txt
files are read directly (used by the demo sample docs). Scanned/photographed
images (.png/.jpg/.jpeg) have no text layer for pypdf/pdfplumber to read, and
classic OCR (Tesseract) handles handwriting and mixed-language text poorly -
those go through a vision-capable LLM (Claude) that transcribes the image
directly instead. (Groq was tried first since it's the same account as the
main LLM, but Groq currently has no vision/multimodal model available - its
/models list is text/audio only - so this uses a separate Anthropic key.)"""
import base64
import logging
import os

import pdfplumber
from anthropic import Anthropic
from pypdf import PdfReader

from app.core.config import settings

logger = logging.getLogger(__name__)

MIN_CHARS_PER_PAGE = 20
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

VISION_OCR_PROMPT = (
    "Transcribe every piece of text visible in this medical document image, "
    "exactly as written, preserving line breaks and table/column structure as "
    "plain text. Include handwritten text - give your best reading even if the "
    "handwriting is messy or the text is in a language other than English. "
    "Output only the transcribed text, with no summary, explanation, or commentary."
)

_anthropic_client: Anthropic | None = None


def _get_anthropic_client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _extract_with_vision(file_path: str) -> tuple[str, float]:
    ext = os.path.splitext(file_path)[1].lower()
    media_type = _MEDIA_TYPES.get(ext, "image/png")
    with open(file_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    client = _get_anthropic_client()
    response = client.messages.create(
        model=settings.ANTHROPIC_VISION_MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
                    },
                    {"type": "text", "text": VISION_OCR_PROMPT},
                ],
            }
        ],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    # Vision transcription doesn't expose a native confidence score; 0.85
    # reflects "generally reliable but not a guaranteed-exact text layer",
    # consistent with the pdfplumber fallback tier below.
    return text, 0.85 if text.strip() else 0.0


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

    if ext in IMAGE_EXTENSIONS:
        try:
            return _extract_with_vision(file_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Vision OCR failed: %s", exc)
            return "", 0.0

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
