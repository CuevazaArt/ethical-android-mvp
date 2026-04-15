"""
Input trust helpers — normalization and light sanitization for MalAbs text matching.

These are **heuristic** defenses against trivial evasions (Unicode tricks, spacing, leet speak,
bidirectional overrides). They are **not** a robust content classifier; see
``docs/proposals/README.md``.
"""

from __future__ import annotations

import os
import re
import unicodedata

# Zero-width and format characters often used to break substring filters.
_ZW_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad]")

# Bidirectional embedding / override — can break contiguous substrings (e.g. RLO inside a word).
_BIDI_EMBED_RE = re.compile("[\u202a-\u202e\u2066-\u2069]")

# C0/C1 controls that should not reach logs or downstream string handling (keep tab/newline).
_UNSAFE_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Common leet / symbol substitutions (single-char fold for lexical MalAbs only).
_LEET_TRANSLATE = str.maketrans(
    {
        "@": "a",
        "4": "a",
        "8": "b",
        "3": "e",
        "1": "i",
        "!": "i",
        "|": "l",
        "0": "o",
        "5": "s",
        "$": "s",
        "7": "t",
        "9": "g",
    }
)

# Common homoglyphs / confusables from Cyrillic and Greek that look like ASCII Latin.
# Applied optionally to MalAbs text to prevent script-mixing bypasses.
_CONFUSABLE_TRANSLATE = str.maketrans(
    {
        "\u0430": "a",
        "\u0435": "e",
        "\u043e": "o",
        "\u0440": "p",
        "\u0441": "c",
        "\u0443": "y",
        "\u0445": "x",
        "\u0456": "i",
        "\u0458": "j",
        "\u0455": "s",
        "\u0432": "b",
        "\u043a": "k",
        "\u043d": "n",
        "\u043c": "m",
        "\u0442": "t",
        "\u03b1": "a",
        "\u03bd": "v",
        "\u03bf": "o",
        "\u03c1": "p",
        "\u03c4": "t",
        "\u03c5": "y",
        "\u03c7": "x",
    }
)


def _leet_fold_enabled() -> bool:
    v = os.environ.get("KERNEL_MALABS_LEET_FOLD", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _bidi_strip_enabled() -> bool:
    v = os.environ.get("KERNEL_MALABS_STRIP_BIDI", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _confusable_fold_enabled() -> bool:
    v = os.environ.get("KERNEL_MALABS_CONFUSABLE_FOLD", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _fold_fullwidth_latin_digits(s: str) -> str:
    """Map fullwidth ASCII alphanumerics (U+FF01–FF5E) to halfwidth where applicable."""
    out: list[str] = []
    for ch in s:
        o = ord(ch)
        if 0xFF01 <= o <= 0xFF5E:
            out.append(chr(o - 0xFEE0))
        elif 0xFF10 <= o <= 0xFF19:
            out.append(chr(0x30 + (o - 0xFF10)))
        else:
            out.append(ch)
    return "".join(out)


def normalize_text_for_malabs(text: str) -> str:
    """
    Normalize user text before conservative substring checks in ``evaluate_chat_text``.

    - Unicode **NFKC** (compatibility composition).
    - Strip zero-width / soft-hyphen characters.
    - Optional: strip **bidirectional overrides** (``KERNEL_MALABS_STRIP_BIDI``, default on).
    - Map **fullwidth** Latin digits/letters to ASCII.
    - Optional: **leet** digit/symbol fold (``KERNEL_MALABS_LEET_FOLD``, default on).
    - Collapse internal whitespace and trim.

    Homoglyphs across scripts (e.g. Cyrillic lookalikes) are not fully resolved; use semantic MalAbs.
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = _ZW_RE.sub("", t)
    if _bidi_strip_enabled():
        t = _BIDI_EMBED_RE.sub("", t)
    t = _fold_fullwidth_latin_digits(t)
    if _confusable_fold_enabled():
        t = t.translate(_CONFUSABLE_TRANSLATE)
    if _leet_fold_enabled():
        t = t.translate(_LEET_TRANSLATE)
    t = " ".join(t.split())
    return t.strip()


def strip_unsafe_perception_text(text: str) -> str:
    """
    Remove ASCII control characters except tab and newline from LLM-derived summary text.

    Perception JSON is untrusted; this limits log/terminal oddities and delimiter tricks.
    """
    if not text:
        return ""
    return _UNSAFE_CTRL_RE.sub("", text)
