"""
OCR Utility — Google Cloud Vision API backend
==============================================
Replaces EasyOCR/Tesseract with Google Vision API:
  - No model downloads (~0 MB added to bundle)
  - Better accuracy than EasyOCR on real documents
  - Free tier: 1000 pages/month

Setup:
  1. Enable "Cloud Vision API" in Google Cloud Console
  2. Create an API key
  3. Set env variable: GOOGLE_VISION_API_KEY=your_key

If no API key is set, falls back to pypdf text extraction only
(images in scanned PDFs will be skipped with a warning).
"""

from __future__ import annotations
import base64
import json
import urllib.request
import urllib.error
from PIL import Image, ImageFilter, ImageEnhance
import io
import os

VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"


def preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image quality before sending to Vision API."""
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.8)
    image = image.filter(ImageFilter.SHARPEN)
    return image


def _image_to_base64(image: Image.Image) -> str:
    """Convert PIL image to base64 string for Vision API."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _call_vision_api(image_b64: str, lang_hints: list[str]) -> str:
    """
    Call Google Cloud Vision API and return detected text.
    Uses DOCUMENT_TEXT_DETECTION for best accuracy on documents.
    """
    api_key = os.environ.get("GOOGLE_VISION_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_VISION_API_KEY environment variable not set.")

    payload = {
        "requests": [{
            "image": {"content": image_b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION", "maxResults": 1}],
            "imageContext": {"languageHints": lang_hints} if lang_hints else {}
        }]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{VISION_API_URL}?key={api_key}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        response = result.get("responses", [{}])[0]
        full_text = response.get("fullTextAnnotation", {}).get("text", "")
        return full_text.strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Vision API error {e.code}: {e.read().decode()}")
    except Exception as e:
        raise RuntimeError(f"Vision API request failed: {e}")


def _parse_lang(lang: str) -> list[str]:
    """
    Convert 'eng+hin+fra' or 'en+hi+fr' to Vision API language hints.
    """
    lang_map = {
        "eng": "en", "en": "en",
        "hin": "hi", "hi": "hi",
        "fra": "fr", "fr": "fr",
    }
    parts = lang.replace(",", "+").split("+")
    return [lang_map.get(p.strip().lower(), p.strip()) for p in parts if p.strip()]


def run_ocr(image: Image.Image, lang: str = "en", preprocess: bool = True) -> str:
    """
    Run OCR on a PIL image using Google Cloud Vision API.

    Args:
        image      : PIL Image (any mode).
        lang       : Language string ('en', 'en+hi+fr', 'eng', etc.)
        preprocess : Apply contrast/sharpening before OCR.

    Returns:
        Extracted text string.

    Raises:
        RuntimeError: If API key is missing or API call fails.
    """
    if preprocess:
        image = preprocess_image(image)

    image_b64 = _image_to_base64(image)
    lang_hints = _parse_lang(lang)
    return _call_vision_api(image_b64, lang_hints)
