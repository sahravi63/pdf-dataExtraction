"""
PDF Text Extraction — Vercel-compatible
========================================
  1. Native text extraction via pypdf (fast, digital PDFs)
  2. Embedded image OCR via Google Vision API (scanned PDFs)

No pdf2image / poppler dependency needed — uses pypdf's
built-in image extraction instead.
"""

from __future__ import annotations
import io
from pypdf import PdfReader
from PIL import Image


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False,
                           ocr_lang: str = "en") -> str:
    """
    Extract all text from a PDF file.

    Args:
        pdf_path : Path to the PDF.
        use_ocr  : If True, OCR embedded images on pages with no text.
        ocr_lang : Language hint for OCR (e.g. 'en', 'en+hi').

    Returns:
        Full extracted text string.
    """
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        raise ValueError(f"Could not open PDF: {e}")

    text_parts = []

    for i, page in enumerate(reader.pages):
        page_text = (page.extract_text() or "").strip()
        if page_text:
            text_parts.append(page_text)
        elif use_ocr:
            # Extract images embedded in the PDF page and OCR them
            try:
                from utils.ocr import run_ocr
                for img_obj in page.images:
                    img = Image.open(io.BytesIO(img_obj.data))
                    ocr_text = run_ocr(img, lang=ocr_lang, preprocess=True)
                    if ocr_text:
                        text_parts.append(ocr_text)
            except Exception as e:
                text_parts.append(f"[OCR failed for page {i+1}: {e}]")

    return "\n".join(text_parts).strip()
