"""
Translation Utility
===================
Translates extracted text into English, Hindi, and French.

Uses deep-translator (GoogleTranslator) as the primary engine.
Falls back gracefully if translation fails — returns original text with an error note.

Supported output languages:
    en  → English
    hi  → Hindi
    fr  → French

Auto-detects source language using langdetect before translating,
so multilingual PDFs / images are handled correctly.

Install:
    pip install deep-translator langdetect
"""

from typing import Dict, Optional

TARGET_LANGUAGES = {
    "English": "en",
    "Hindi":   "hi",
    "French":  "fr",
}

# Max chars per chunk — Google Translate free tier limit is ~5000
_CHUNK_SIZE = 4500


def _detect_language(text: str) -> str:
    """Return ISO language code of the text, default 'auto'."""
    try:
        from langdetect import detect
        return detect(text)
    except Exception:
        return "auto"


def _split_chunks(text: str, size: int = _CHUNK_SIZE):
    """Split text into chunks at paragraph boundaries where possible."""
    if len(text) <= size:
        yield text
        return
    paragraphs = text.split("\n")
    chunk = ""
    for para in paragraphs:
        if len(chunk) + len(para) + 1 > size:
            if chunk:
                yield chunk
            chunk = para
        else:
            chunk = (chunk + "\n" + para) if chunk else para
    if chunk:
        yield chunk


def _translate_chunk(chunk: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate a single chunk using deep-translator."""
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    return translator.translate(chunk)


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate *text* to *target_lang*.

    Args:
        text        : Input text (any language).
        target_lang : ISO 639-1 code, e.g. 'en', 'hi', 'fr'.

    Returns:
        Translated string, or original text with error message prepended on failure.
    """
    if not text or not text.strip():
        return text

    try:
        source_lang = _detect_language(text)
        # Skip translation if already in target language
        if source_lang == target_lang:
            return text

        translated_chunks = []
        for chunk in _split_chunks(text):
            translated_chunks.append(
                _translate_chunk(chunk, target_lang=target_lang, source_lang=source_lang)
            )
        return "\n".join(translated_chunks)

    except ImportError:
        return (
            f"[Translation unavailable — install: pip install deep-translator langdetect]\n\n"
            f"{text}"
        )
    except Exception as e:
        return f"[Translation error: {e}]\n\n{text}"


def translate_all(text: str) -> Dict[str, str]:
    """
    Translate *text* into all three output languages.

    Returns:
        Dict with keys 'English', 'Hindi', 'French' and translated values.
    """
    results = {}
    for lang_name, lang_code in TARGET_LANGUAGES.items():
        results[lang_name] = translate_text(text, target_lang=lang_code)
    return results
