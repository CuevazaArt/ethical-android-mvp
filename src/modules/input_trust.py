"""
Input trust helpers — normalization and light sanitization for MalAbs text matching.

These are **heuristic** defenses against trivial evasions (Unicode tricks, spacing).
They are **not** a robust content classifier; see ``docs/INPUT_TRUST_THREAT_MODEL.md``.
"""

import re
import unicodedata


# Zero-width and format characters often used to break substring filters.
_ZW_RE = re.compile(
    "[\u200b\u200c\u200d\u2060\ufeff\u00ad]"
)


def normalize_text_for_malabs(text: str) -> str:
    """
    Normalize user text before conservative substring checks in ``evaluate_chat_text``.

    - Applies Unicode **NFKC** (compatibility composition).
    - Strips zero-width / soft-hyphen characters.
    - Collapses internal whitespace to a single space and trims ends.

    Does not remove all homoglyphs or leetspeak; phrase lists must still evolve.
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = _ZW_RE.sub("", t)
    t = " ".join(t.split())
    return t.strip()
