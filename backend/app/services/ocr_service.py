"""Text extraction: pypdf primary, pdfplumber fallback for PDFs; plain .txt
files are read directly (used by the demo sample docs). Neither library does
true OCR - real-world uploads are frequently scanned/photographed documents
with no text layer at all (a native image upload, or a PDF that's just a
picture exported/printed to PDF, which looks identical to pypdf/pdfplumber:
zero extractable text). Those go through Gemini (Google's vision-capable
LLM), which transcribes the image directly instead."""
import base64
import io
import logging
import os

import pdfplumber
import pypdfium2 as pdfium
from google import genai
from pypdf import PdfReader

from app.core.config import settings

logger = logging.getLogger(__name__)

MIN_CHARS_PER_PAGE = 20
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
MAX_VISION_PDF_PAGES = 5

VISION_OCR_PROMPT = (
    "Transcribe every piece of text visible in this medical document image, "
    "exactly as written, preserving line breaks and table/column structure as "
    "plain text. Include handwritten text - give your best reading even if the "
    "handwriting is messy or the text is in a language other than English. "
    "Output only the transcribed text, with no summary, explanation, or commentary."
)

_gemini_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _gemini_client


def _call_vision_model(image_bytes: bytes, mime_type: str) -> str:
    client = _get_gemini_client()
    interaction = client.interactions.create(
        model=settings.GEMINI_VISION_MODEL,
        input=[
            {"type": "text", "text": VISION_OCR_PROMPT},
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
                "mime_type": mime_type,
            },
        ],
    )
    return interaction.output_text or ""


def _extract_with_vision(file_path: str) -> tuple[str, float]:
    ext = os.path.splitext(file_path)[1].lower()
    media_type = _MEDIA_TYPES.get(ext, "image/png")
    with open(file_path, "rb") as f:
        image_bytes = f.read()
    text = _call_vision_model(image_bytes, media_type)
    # Vision transcription doesn't expose a native confidence score; 0.85
    # reflects "generally reliable but not a guaranteed-exact text layer",
    # consistent with the pdfplumber fallback tier below.
    return text, 0.85 if text.strip() else 0.0


def _extract_pdf_with_vision(file_path: str) -> str:
    """Renders each PDF page to an image and OCRs it with the vision model -
    the fallback for scanned/photographed PDFs (e.g. an image exported or
    printed to PDF) that have no real text layer for pypdf/pdfplumber to read."""
    pdf = pdfium.PdfDocument(file_path)
    try:
        page_texts = []
        for i in range(min(len(pdf), MAX_VISION_PDF_PAGES)):
            bitmap = pdf[i].render(scale=2.0)
            buf = io.BytesIO()
            bitmap.to_pil().save(buf, format="PNG")
            page_texts.append(_call_vision_model(buf.getvalue(), "image/png"))
        return "\n\n".join(t for t in page_texts if t.strip())
    finally:
        pdf.close()


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
            text, page_count = fallback_text, fallback_pages
    except Exception as exc:  # noqa: BLE001
        logger.warning("pdfplumber fallback failed: %s", exc)

    if page_count and len(text) / page_count >= MIN_CHARS_PER_PAGE:
        return text, 0.75

    # Both text-layer extractors came back empty/near-empty - this is very
    # likely a scanned/photographed document with no real text layer (e.g.
    # an image exported to PDF). Render the pages and OCR them with the
    # vision model, same as a native image upload.
    try:
        vision_text = _extract_pdf_with_vision(file_path)
        if vision_text.strip():
            return vision_text, 0.85
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDF vision OCR fallback failed: %s", exc)

    return text, 0.3 if text.strip() else 0.0
