"""
Data Masking Utility
====================
Masks 4 sensitive data types + URLs, with labelled partial masking:

  rsahravi57@gmail.com       →  [EMAIL] ****@gmail.com
  +91 9234614488             →  [PHONE] +91 ****
  Ravi Sah                   →  [NAME] ****
  4111 1111 1111 1111        →  [CARD] **** 1111
  github.com/sahravi63        →  [URL] github.com/****
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# ── Regex patterns ─────────────────────────────────────────────────────────

_PATTERNS: List[Tuple[str, str]] = [
    ("CARD",
     r'\b(?:4[0-9]{12}(?:[0-9]{3})?'
     r'|5[1-5][0-9]{14}'
     r'|3[47][0-9]{13}'
     r'|3(?:0[0-5]|[68][0-9])[0-9]{11}'
     r'|6(?:011|5[0-9]{2})[0-9]{12}'
     r'|(?:[0-9]{4}[- ]){3}[0-9]{4})\b'),

    ("EMAIL",
     r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'),

    ("PHONE",
     r'(?<!\d)'
     r'(?:\+\d{1,3}[\s\-.]?)?'
     r'(?:\(?\d{3,5}\)?[\s\-.]?)'
     r'\d{3,5}[\s\-.]?\d{3,5}'
     r'(?!\d)'),

    ("URL",
     r'(?:https?://|www\.)[^\s<>"\']+'
     r'|(?:github\.com|linkedin\.com|twitter\.com|facebook\.com)/[^\s<>"\']+'),
]

_NAME_FALLBACK_RE = re.compile(
    r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})', re.MULTILINE
)


# ── Partial masking: label + keep safe portion ─────────────────────────────

def _mask_value(label: str, original: str) -> str:
    """
    Return a labelled, partially masked string for each type.
    """
    if label == "EMAIL":
        # rsahravi57@gmail.com  →  [EMAIL] ****@gmail.com
        if "@" in original:
            _, domain = original.split("@", 1)
            return f"[EMAIL] ****@{domain}"
        return "[EMAIL] ****"

    if label == "PHONE":
        # +91 9234614488  →  [PHONE] +91 ****
        m = re.match(r'(\+\d{1,3}[\s\-.]?)(.*)', original)
        if m:
            return f"[PHONE] {m.group(1).strip()} ****"
        return "[PHONE] ****"

    if label == "CARD":
        # 4111 1111 1111 1111  →  [CARD] **** 1111
        digits = re.sub(r'\D', '', original)
        last4 = digits[-4:] if len(digits) >= 4 else digits
        return f"[CARD] **** {last4}"

    if label == "NAME":
        # Ravi Sah  →  [NAME] ****
        return "[NAME] ****"

    if label == "URL":
        # github.com/sahravi63  →  [URL] github.com/****
        m = re.match(r'((?:https?://)?(?:www\.)?[^/\s]+)(.*)', original)
        if m:
            return f"[URL] {m.group(1)}/****"
        return "[URL] ****"

    return f"[{label}] ****"


# ── Data classes ───────────────────────────────────────────────────────────

@dataclass
class MaskedSpan:
    original:    str
    label:       str
    replacement: str
    start:       int
    end:         int
    source:      str


@dataclass
class MaskReport:
    total_masked: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)

    def add(self, label: str):
        self.total_masked += 1
        self.by_type[label] = self.by_type.get(label, 0) + 1


# ── Span collectors ────────────────────────────────────────────────────────

def _collect_regex_spans(text: str) -> List[MaskedSpan]:
    spans = []
    for label, pattern in _PATTERNS:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            original = m.group()
            spans.append(MaskedSpan(
                original=original,
                label=label,
                replacement=_mask_value(label, original),
                start=m.start(),
                end=m.end(),
                source='regex',
            ))
    return spans


def _collect_name_spans(text: str) -> List[MaskedSpan]:
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        return [
            MaskedSpan(
                original=ent.text,
                label='NAME',
                replacement=_mask_value('NAME', ent.text),
                start=ent.start_char,
                end=ent.end_char,
                source='ner',
            )
            for ent in doc.ents if ent.label_ == 'PERSON'
        ]
    except Exception:
        pass

    # Regex fallback — first capitalised "Firstname Lastname" line
    spans = []
    for m in _NAME_FALLBACK_RE.finditer(text):
        original = m.group(1)
        spans.append(MaskedSpan(
            original=original,
            label='NAME',
            replacement=_mask_value('NAME', original),
            start=m.start(1),
            end=m.end(1),
            source='fallback',
        ))
        break
    return spans


def _resolve_overlaps(spans: List[MaskedSpan]) -> List[MaskedSpan]:
    spans = sorted(spans, key=lambda s: (s.start, -(s.end - s.start)))
    resolved, last_end = [], -1
    for span in spans:
        if span.start >= last_end:
            resolved.append(span)
            last_end = span.end
    return resolved


# ── Public API ─────────────────────────────────────────────────────────────

def mask_text(text: str):
    """
    Detect and replace sensitive data with labelled partial masks.

    Returns:
        (masked_text: str, report: MaskReport)
    """
    if not text:
        return text, MaskReport()

    all_spans = _collect_regex_spans(text) + _collect_name_spans(text)
    resolved  = _resolve_overlaps(all_spans)

    report = MaskReport()
    # Build result by splicing replacements back-to-front
    result = text
    for span in reversed(resolved):
        result = result[:span.start] + span.replacement + result[span.end:]
        report.add(span.label)

    return result, report


def get_mask_summary(report: MaskReport) -> str:
    if report.total_masked == 0:
        return "No sensitive data detected."
    parts = [f"{label} ×{count}" for label, count in sorted(report.by_type.items())]
    return f"Masked {report.total_masked} item(s): " + ", ".join(parts)
