"""
Image Text Extraction — EasyOCR backend
========================================
Extracts text from image files using EasyOCR (no Tesseract needed).

Supported formats: .jpg .jpeg .png .webp .bmp .tiff .tif
"""

import os
from PIL import Image
from utils.ocr import run_ocr

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


def is_image_file(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in SUPPORTED_EXTENSIONS


def extract_text_from_image(image_path: str, ocr_lang: str = "eng") -> str:
    """
    Open an image file and extract text using EasyOCR.

    Args:
        image_path : Path to the image file.
        ocr_lang   : Language string, e.g. 'eng', 'eng+hin+fra'.

    Returns:
        Extracted text string.

    Raises:
        ValueError  : Unsupported file format.
        RuntimeError: EasyOCR not installed or read failure.
    """
    ext = os.path.splitext(image_path.lower())[1]
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    try:
        image = Image.open(image_path)
        if image.mode not in ("RGB", "L", "RGBA"):
            image = image.convert("RGB")
        return run_ocr(image, lang=ocr_lang, preprocess=True)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to read image '{os.path.basename(image_path)}': {e}")
