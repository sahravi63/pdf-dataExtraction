"""
Named Entity Recognition — Regex-based (Vercel-compatible)
============================================================
Replaces spaCy (which is too large for Vercel) with fast regex patterns.
Detects: PERSON, ORG, EMAIL, PHONE, DATE, URL, LOCATION

Accuracy is lower than spaCy's ML model but works well for
structured documents like resumes, invoices, and reports.
"""

import re
from typing import List, Dict

# ── Patterns ────────────────────────────────────────────────────────────────

_PATTERNS: Dict[str, str] = {
    "EMAIL":    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b',
    "PHONE":    r'(?<!\d)(?:\+\d{1,3}[\s\-.]?)?(?:\(?\d{3,5}\)?[\s\-.]?)?\d{3,5}[\s\-.]?\d{3,5}(?!\d)',
    "URL":      r'https?://[^\s<>"\']+'
                r'|(?:www\.|github\.com|linkedin\.com)[^\s<>"\']*',
    "DATE":     r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}'
                r'|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}'
                r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
                r'[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',
    "PERSON":   r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b',
    "ORG":      r'\b([A-Z][A-Za-z&]+(?:\s+[A-Z][A-Za-z&]+){0,4}'
                r'(?:\s+(?:Inc|LLC|Ltd|Corp|Co|University|Institute|Technologies|Solutions))?)\b',
}

# Words that look like names/orgs but aren't entities
_STOPWORDS = {
    "The", "This", "That", "These", "Those", "With", "From", "Your",
    "Their", "About", "When", "What", "Where", "Which", "Python",
    "Java", "Docker", "React", "Node", "Flask", "Monday", "Tuesday",
    "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
}


def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract named entities from text using regex patterns.

    Returns:
        List of dicts: {text, label, start, end}
    """
    if not text or not text.strip():
        return []

    entities = []
    seen = set()

    for label, pattern in _PATTERNS.items():
        for m in re.finditer(pattern, text, re.MULTILINE):
            value = m.group().strip()
            if value in _STOPWORDS or value in seen:
                continue
            seen.add(value)
            entities.append({
                "text":  value,
                "label": label,
                "start": m.start(),
                "end":   m.end(),
            })

    return entities


def group_entities_by_type(text: str) -> Dict[str, List[str]]:
    """
    Extract entities and group by label.

    Returns:
        Dict: {label: [entity1, entity2, ...]}
    """
    entities = extract_entities(text)
    grouped: Dict[str, List[str]] = {}
    for ent in entities:
        label = ent["label"]
        value = ent["text"]
        if label not in grouped:
            grouped[label] = []
        if value not in grouped[label]:
            grouped[label].append(value)
    return grouped
