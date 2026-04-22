"""
Input trust helpers — normalization and light sanitization for MalAbs text matching.

These are **heuristic** defenses against trivial evasions (Unicode tricks, spacing, leet speak,
bidirectional overrides). They are **not** a robust content classifier; see
``docs/proposals/README.md``.
"""
# Status: SCAFFOLD


from __future__ import annotations

import logging
import os
import re
import time
import unicodedata

_log = logging.getLogger(__name__)

# Zero-width and format characters often used to break substring filters.
_ZW_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad]")

# Swarm Safe: Maximum string length to prevent DoS in normalization loops.
MAX_TEXT_LENGTH = int(os.environ.get("KERNEL_INPUT_MAX_LENGTH", "10000"))

# Bidirectional embedding / override — can break contiguous substrings (e.g. RLO inside a word).
# Includes more comprehensive bidi control characters (U+202A-U+202E, U+2066-U+2069).
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
        "\u0410": "A",  # Cyrillic A
        "\u0435": "e",  # Cyrillic e
        "\u0415": "E",  # Cyrillic E
        "\u043e": "o",  # Cyrillic o
        "\u041e": "O",  # Cyrillic O
        "\u0440": "p",  # Cyrillic p
        "\u0420": "P",  # Cyrillic P
        "\u0441": "c",  # Cyrillic c
        "\u0421": "C",  # Cyrillic C
        "\u0443": "y",  # Cyrillic y
        "\u0423": "Y",  # Cyrillic Y
        "\u0445": "x",  # Cyrillic x
        "\u0425": "X",  # Cyrillic X
        "\u0456": "i",  # Cyrillic i
        "\u0416": "K",  # Cyrillic K lookalike? No, Cyrillic K is \u041a
        "\u041a": "K",  # Cyrillic K
        "\u043a": "k",  # Cyrillic k
        "\u041c": "M",  # Cyrillic M
        "\u043c": "m",  # Cyrillic m
        "\u041d": "H",  # Cyrillic N looks like H
        "\u043d": "n",  # Cyrillic n
        "\u0422": "T",  # Cyrillic T
        "\u0442": "t",  # Cyrillic t
        "\u0412": "B",  # Cyrillic B
        "\u0432": "b",  # Cyrillic b
        "\u0458": "j",  # Cyrillic j
        "\u0455": "s",  # Cyrillic s
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
        "\u0130": "I",  # Turkish dotted I
        "\u0131": "i",  # Turkish dotless i
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
    Collapse sequences of 3+ same characters into 2 (e.g. 'booom' -> 'bom', but 'kill' -> 'kill').
    Used to catch 'letter padding' evasions in MalAbs without breaking legitimate doubled letters.
    """
    if not text:
        return ""
    try:
        # Only collapse when 3+ repetitions (preserve legitimate doubled letters like 'kill', 'success')
        return re.sub(r"(.)\1{2,}", r"\1\1", text)
    except Exception:
        return text


def strip_diacritics(text: str) -> str:
    """
    Remove all non-spacing marks (diacritics) from text.
    'hòw' -> 'how', 'étos' -> 'etos'
    """
    if not text:
        return ""
    try:
        # Decompose into base + diacritics
        nfd = unicodedata.normalize("NFD", text)
        # Strip non-spacing marks (category Mn)
        return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    except Exception:
        return text


def strip_bidi_marks(text: str) -> str:
    """Remove bidirectional override and embedding marks."""
    if not text:
        return ""
    try:
        return _BIDI_EMBED_RE.sub("", str(text))
    except Exception:
        return str(text)


def squash_text_for_malabs(text: str) -> str:
    """
    Remove ALL whitespace, punctuation, and diacritics for 'base-ASCII' squashed matching.
    e.g. 'b-ó-m-b' -> 'bomb'
    """
    if not text:
        return ""
    try:
        # 1. Strip marks
        stripped = strip_diacritics(text)
        # 2. Remove all non-alphanumeric (strictly ASCII Latin for lexical layer)
        return re.sub(r"[^a-zA-Z0-9]", "", stripped).lower()
    except Exception:
        return str(text).lower()


def normalize_text_for_malabs(text: str, squash: bool = False) -> str:
    """
    Normalize user text before conservative substring checks in ``evaluate_chat_text``.
    """
    if text is None:
        return ""

    # Boy Scout: Proactive type conversion and DoS Protection
    raw_text = str(text)
    if len(raw_text) > MAX_TEXT_LENGTH:
        _log.warning("InputTrust: Text exceeds MAX_TEXT_LENGTH (%d). Truncating.", MAX_TEXT_LENGTH)
        raw_text = raw_text[:MAX_TEXT_LENGTH]

    t0 = time.perf_counter()
    try:
        t = unicodedata.normalize("NFKC", raw_text)
        try:
            t = _ZW_RE.sub("", t)
            t = _UNSAFE_CTRL_RE.sub("", t)
            if _bidi_strip_enabled():
                t = _BIDI_EMBED_RE.sub("", t)
        except Exception:
            pass

        t = _fold_fullwidth_latin_digits(t)
        if _confusable_fold_enabled():
            t = t.translate(_CONFUSABLE_TRANSLATE)
        if _leet_fold_enabled():
            t = t.translate(_LEET_TRANSLATE)

        if squash:
            return squash_text_for_malabs(t)

        # Collapse repeated characters
        t = collapse_repeated_chars(t)

        t = " ".join(t.split())

        latency = (time.perf_counter() - t0) * 1000
        if latency > 1.0:
            _log.debug("InputTrust: normalize latency = %.2fms", latency)

        return t.strip()
    except Exception as e:
        _log.error("InputTrust: normalization panic: %s", e)
        return raw_text.strip()


def strip_unsafe_perception_text(text: str) -> str:
    """
    Remove ASCII control characters except tab and newline from LLM-derived summary text.

    Perception JSON is untrusted; this limits log/terminal oddities and delimiter tricks.
    """
    if not text:
        return ""
    return _UNSAFE_CTRL_RE.sub("", text)
