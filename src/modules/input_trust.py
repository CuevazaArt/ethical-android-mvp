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
        "6": "g",
        "2": "z",
        "(": "c",
        "[": "c",
        "{": "c",
        "<": "c",
    }
)

# Common homoglyphs / confusables from Cyrillic and Greek that look like ASCII Latin.
# Applied optionally to MalAbs text to prevent script-mixing bypasses.
_CONFUSABLE_TRANSLATE = str.maketrans(
    {
        "\u0430": "a",  # Cyrillic a
        "\u0435": "e",  # Cyrillic e
        "\u043e": "o",  # Cyrillic o
        "\u0440": "p",  # Cyrillic p
        "\u0441": "c",  # Cyrillic c
        "\u0443": "y",  # Cyrillic y
        "\u0445": "x",  # Cyrillic x
        "\u0456": "i",  # Cyrillic i
        "\u0458": "j",  # Cyrillic j
        "\u0455": "s",  # Cyrillic s
        "\u0432": "b",  # Cyrillic b
        "\u043a": "k",  # Cyrillic k
        "\u043d": "n",  # Cyrillic n
        "\u043c": "m",  # Cyrillic m
        "\u0442": "t",  # Cyrillic t
        "\u03b1": "a",  # Greek alpha
        "\u03bd": "v",  # Greek nu
        "\u03bf": "o",  # Greek omicron
        "\u03c1": "p",  # Greek rho
        "\u03c4": "t",  # Greek tau
        "\u03c5": "y",  # Greek upsilon
        "\u03c7": "x",  # Greek chi
        "\u13aa": "j",  # Cherokee j
        "\u13d4": "m",  # Cherokee m
        "\u04cf": "l",  # Cyrillic palochka
        "\u01c0": "l",  # Dental click
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


def collapse_repeated_chars(text: str) -> str:
    """
    Collapse sequences of the same character into a single one (e.g. 'booom' -> 'bom').
    Used to catch 'letter padding' evasions in MalAbs.
    """
    if not text:
        return ""
    # Simple regex for backreference to match repeated chars
    return re.sub(r"(.)\1+", r"\1", text)


def squash_text_for_malabs(text: str) -> str:
    """
    Remove ALL whitespace, punctuation, and diacritics for 'base-ASCII' squashed matching.
    e.g. 'b-ó-m-b' -> 'bomb'
    """
    if not text:
        return ""
    # 1. Decompose into base + diacritics
    nfd = unicodedata.normalize("NFD", text)
    # 2. Strip non-spacing marks (diacritics)
    stripped = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    # 3. Remove all non-alphanumeric (strictly ASCII Latin for lexical layer)
    return re.sub(r"[^a-zA-Z0-9]", "", stripped).lower()


def normalize_text_for_malabs(text: str, squash: bool = False) -> str:
    """
    Normalize user text before conservative substring checks in ``evaluate_chat_text``.

    - Unicode **NFKC** (compatibility composition).
    - Strip zero-width / soft-hyphen characters.
    - Optional: strip **bidirectional overrides** (``KERNEL_MALABS_STRIP_BIDI``, default on).
    - Map **fullwidth** Latin digits/letters to ASCII.
    - Optional: **leet** digit/symbol fold (``KERNEL_MALABS_LEET_FOLD``, default on).
    - Optional: **confusable** folding (Cyrillic, Greek, etc., default on).
    - Collapse repeated characters (e.g. 'bbbooommm' -> 'bom').
    - Collapse internal whitespace and trim.

    Homoglyphs across scripts (e.g. Cyrillic lookalikes) are mostly resolved; use semantic MalAbs
    for complex paraphrases.
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

    if squash:
        return squash_text_for_malabs(t)

    # Collapse repeated characters (after folding to ensure things like '@a' -> 'aa' -> 'a' work)
    t = collapse_repeated_chars(t)

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
