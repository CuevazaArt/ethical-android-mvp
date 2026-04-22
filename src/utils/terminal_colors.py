"""
ANSI helpers for operator-facing CLI output (kernel demo, ``format_decision``, summaries).

Environment:

- ``KERNEL_TERM_COLOR`` — ``0`` disables escape sequences (plain text); default ``1``.
- ``NO_COLOR`` — if present in the environment, disables color (https://no-color.org/),
  regardless of ``KERNEL_TERM_COLOR`` (CI logs, pipes, accessibility).
"""

from __future__ import annotations

import logging
import math
import operator
import os
import sys

_STD_OUTPUT_HANDLE = -11
_ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
_log = logging.getLogger(__name__)

# Operator / tests: ``Term`` is the public API; width helpers keep demo scripts aligned with
# the same anti-DoS / finitude rules as :meth:`Term.header` (V4.0 / Pragmatismo).
__all__ = ("Term", "_DEFAULT_SEP_WIDTH", "_MAX_HEADER_BAR", "_clamped_header_bar_width")

# ``Term.header`` bar length cap (operator / demo scripts; avoids pathological ``"═" * n``).
_MAX_HEADER_BAR = 512
# Default class separator width (rules + :meth:`Term.header`); single source to avoid magic ``70`` drift.
# Exported in :data:`__all__` for operator scripts and integration gates (same value as :attr:`Term.SEP_WIDTH` on the base class).
_DEFAULT_SEP_WIDTH = 70


def _saturate_bar_width(n: int) -> int:
    """Integral bar width in ``[1, _MAX_HEADER_BAR]`` (all exit paths, including *default*)."""
    return min(_MAX_HEADER_BAR, max(1, n))


def _clamped_header_bar_width(raw: object, *, default: int) -> int:
    """
    Coerce to a positive integral width capped at :data:`_MAX_HEADER_BAR`.

    Rejects non-finite floats, ``bool``/``None`` (``True`` must not become width ``1``), and
    string forms that do not parse to a finite scalar. The **plain ``int``** path never calls
    ``float(n)`` on the width: huge integers would otherwise turn into ``inf`` and erase the
    bar (V4.0 / Harden-In-Place).

    Fallbacks that return *default* are passed through :func:`_saturate_bar_width` so callers
    cannot bypass the cap with an oversized *default* (8.1.27).
    """
    if isinstance(raw, bool) or raw is None:
        return _saturate_bar_width(default)
    if isinstance(raw, int):
        w = raw
        if w < 1:
            w = 1
        return _saturate_bar_width(w)
    if isinstance(raw, float):
        if not math.isfinite(raw):
            return _saturate_bar_width(default)
        try:
            w = int(raw)
        except (TypeError, ValueError, OverflowError):
            return _saturate_bar_width(default)
        if w < 1:
            w = 1
        return _saturate_bar_width(w)
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return _saturate_bar_width(default)
        try:
            f = float(s)
        except (TypeError, ValueError, OverflowError):
            return _saturate_bar_width(default)
        if not math.isfinite(f):
            return _saturate_bar_width(default)
        try:
            w = int(f)
        except (TypeError, ValueError, OverflowError):
            return _saturate_bar_width(default)
        if w < 1:
            w = 1
        return _saturate_bar_width(w)
    try:
        w = operator.index(raw)
    except (TypeError, ValueError, OverflowError):
        return _saturate_bar_width(default)
    if w < 1:
        w = 1
    return _saturate_bar_width(w)


def _enable_windows_ansi() -> None:
    """Enable ANSI escape processing on Windows 10+ consoles (VT mode)."""
    if sys.platform != "win32":
        return
    import ctypes

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(_STD_OUTPUT_HANDLE)
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return
    kernel32.SetConsoleMode(handle, mode.value | _ENABLE_VIRTUAL_TERMINAL_PROCESSING)


def _colors_enabled() -> bool:
    """True when escape codes may be emitted (honours ``NO_COLOR`` + ``KERNEL_TERM_COLOR``)."""
    if "NO_COLOR" in os.environ:
        return False
    return os.environ.get("KERNEL_TERM_COLOR", "1") != "0"


if _colors_enabled():
    try:
        _enable_windows_ansi()
    except (OSError, AttributeError, TypeError, ValueError) as exc:
        # Best-effort VT: missing APIs, headless, or old consoles — never fail import.
        _log.debug(
            "Windows VT ANSI not enabled (continuing with plain or stripped output): %s", exc
        )


class Term:
    """ANSI color codes for the Ethos Kernel."""

    SEP_WIDTH = _DEFAULT_SEP_WIDTH

    # Text colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    B_RED = "\033[91m"
    B_GREEN = "\033[92m"
    B_YELLOW = "\033[93m"
    B_BLUE = "\033[94m"
    B_MAGENTA = "\033[95m"
    B_CYAN = "\033[96m"
    B_WHITE = "\033[97m"

    # Backgrounds
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"

    @classmethod
    def color(cls, text: object, color_code: str) -> str:
        """
        Wrap *text* with *color_code* and :attr:`RESET`.

        *text* is ``object`` (kernel / demos may pass numbers); coerced with :func:`str`
        when not already a :class:`str` — same idea as :meth:`header` / :meth:`subheader`.
        If coercion fails, emits ``"?"`` (Pragmatismo / no crash on pathological ``__str__``).
        """
        try:
            t = text if isinstance(text, str) else str(text)
        except (TypeError, ValueError):
            t = "?"
        if not _colors_enabled():
            return t
        return f"{color_code}{t}{cls.RESET}"

    @classmethod
    def _rule_width(cls) -> int:
        """Like :meth:`header` — same cap as :func:`_clamped_header_bar_width` (subclass ``SEP_WIDTH``)."""
        return _clamped_header_bar_width(
            getattr(cls, "SEP_WIDTH", _DEFAULT_SEP_WIDTH),
            default=_DEFAULT_SEP_WIDTH,
        )

    @classmethod
    def rule_heavy(cls, *, width: int | float | str | None = None) -> str:
        """Full-width strong separator (section boundaries in operator debug output)."""
        w = (
            _clamped_header_bar_width(width, default=cls._rule_width())
            if width is not None
            else cls._rule_width()
        )
        return cls.color("=" * w, cls.DIM)

    @classmethod
    def rule_light(cls, *, width: int | float | str | None = None) -> str:
        """Full-width light separator."""
        w = (
            _clamped_header_bar_width(width, default=cls._rule_width())
            if width is not None
            else cls._rule_width()
        )
        return cls.color("-" * w, cls.DIM)

    @classmethod
    def highlight_decision(cls, mode: object) -> str:
        """
        Color known decision-mode labels from the kernel. Unknown / empty labels
        are still shown (default emphasis); whitespace-only or unusable input → dim ``?``.

        ``mode`` is ``object`` (kernel may pass ``None`` or non-``str`` labels); coercion
        is best-effort, same contract as :meth:`highlight_impact`.
        """
        try:
            s = str(mode).strip() if mode is not None else ""
        except (TypeError, ValueError):
            s = ""
        if not s:
            return cls.color("?", cls.DIM)
        if s == "D_fast":
            return cls.color(s, cls.B_GREEN + cls.BOLD)
        if s == "D_delib":
            return cls.color(s, cls.B_CYAN + cls.BOLD)
        if s == "gray_zone":
            return cls.color(s, cls.B_YELLOW + cls.BOLD)
        return cls.color(s, cls.BOLD)

    @classmethod
    def highlight_impact(cls, val: object) -> str:
        """Format expected impact; non-finite values are shown dimmed (no misleading hue ladder)."""
        try:
            v = float(val)
        except (TypeError, ValueError, OverflowError):
            return cls.color("?", cls.DIM)
        if not math.isfinite(v):
            return cls.color(f"{v:+.3f}", cls.DIM)
        color = cls.RESET
        if v > 0.5:
            color = cls.B_GREEN
        elif v > 0.1:
            color = cls.GREEN
        elif v < -0.5:
            color = cls.B_RED
        elif v < -0.1:
            color = cls.RED
        return cls.color(f"{v:+.3f}", color)

    @classmethod
    def header(
        cls,
        title: object,
        *,
        width: int | float | str | None = None,
    ) -> str:
        """Primary section block (demo summaries, operator debug).

        *title* is coerced like :meth:`subheader` / :meth:`highlight_decision` (8.1.28 / 8.1.20).

        When *width* is ``None`` (the default), uses :meth:`_rule_width` — same subclass-aware
        bar length as :meth:`rule_heavy` / :meth:`rule_light` (not a frozen module literal).
        Otherwise *width* is passed to :func:`_clamped_header_bar_width` with
        ``default=cls._rule_width()`` (invalid *width* may resolve to *default* verbatim, so
        the default must be clamped like the nominal bar width, not an uncapped ``SEP_WIDTH``).
        """
        if width is None:
            w = cls._rule_width()
        else:
            w = _clamped_header_bar_width(width, default=cls._rule_width())
        try:
            t = str(title).strip() if title is not None else ""
        except (TypeError, ValueError):
            t = ""
        if not t:
            t = "?"
        bar = cls.color("═" * w, cls.DIM)
        line = f"  {cls.color(t, cls.B_CYAN + cls.BOLD)}"
        return f"\n{bar}\n{line}\n{bar}"

    @classmethod
    def subheader(cls, title: object) -> str:
        """Secondary section line under a header (operator demo; *title* coerced like :meth:`highlight_decision`)."""
        try:
            s = str(title).strip() if title is not None else ""
        except (TypeError, ValueError):
            s = ""
        prefix = cls.color("▸", cls.DIM)
        if not s:
            label = cls.color("?", cls.DIM)
        else:
            label = cls.color(s, cls.CYAN + cls.BOLD)
        return f"\n  {prefix} {label}"
