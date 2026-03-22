"""
Image Processing Utilities
===========================
Preprocessing helpers used before passing images to EasyOCR.
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import io


def load_image_from_bytes(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def resize_image(image: Image.Image, max_width: int = 2000,
                 max_height: int = 2000) -> Image.Image:
    """Resize preserving aspect ratio so neither dimension exceeds max."""
    image.thumbnail((max_width, max_height), Image.LANCZOS)
    return image


def deskew_image(image: Image.Image) -> Image.Image:
    """Apply EXIF orientation correction."""
    return ImageOps.exif_transpose(image)


def binarize_image(image: Image.Image, threshold: int = 128) -> Image.Image:
    """Convert to pure black-and-white using a fixed threshold."""
    gray = image.convert("L")
    return gray.point(lambda p: 255 if p > threshold else 0, "1")


def enhance_for_ocr(image: Image.Image) -> Image.Image:
    """
    Standard enhancement pipeline for EasyOCR accuracy:
      grayscale → contrast boost → sharpen → median denoise
    """
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    return image


def crop_margins(image: Image.Image, margin_px: int = 10) -> Image.Image:
    """Crop a fixed-pixel margin from all sides (removes scanner borders)."""
    w, h = image.size
    left, top = margin_px, margin_px
    right  = max(w - margin_px, left + 1)
    bottom = max(h - margin_px, top + 1)
    return image.crop((left, top, right, bottom))
