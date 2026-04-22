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

# Operator / tests: ``Term`` is the public API; bar cap is exposed for integration assertions.
__all__ = ("Term", "_MAX_HEADER_BAR")

# ``Term.header`` bar length cap (operator / demo scripts; avoids pathological ``"═" * n``).
_MAX_HEADER_BAR = 512


def _clamped_header_bar_width(raw: object, *, default: int) -> int:
    """
    Coerce to a positive integral width capped at :data:`_MAX_HEADER_BAR`.

    Rejects non-finite floats, ``bool``/``None`` (``True`` must not become width ``1``), and
    string forms that do not parse to a finite scalar. The **plain ``int``** path never calls
    ``float(n)`` on the width: huge integers would otherwise turn into ``inf`` and erase the
    bar (V4.0 / Harden-In-Place).
    """
    if isinstance(raw, bool) or raw is None:
        return default
    if isinstance(raw, int):
        w = raw
        if w < 1:
            w = 1
        return min(_MAX_HEADER_BAR, w)
    if isinstance(raw, float):
        if not math.isfinite(raw):
            return default
        try:
            w = int(raw)
        except (TypeError, ValueError, OverflowError):
            return default
        if w < 1:
            w = 1
        return min(_MAX_HEADER_BAR, w)
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return default
        try:
            f = float(s)
        except (TypeError, ValueError, OverflowError):
            return default
        if not math.isfinite(f):
            return default
        try:
            w = int(f)
        except (TypeError, ValueError, OverflowError):
            return default
        if w < 1:
            w = 1
        return min(_MAX_HEADER_BAR, w)
    try:
        w = operator.index(raw)
    except (TypeError, ValueError, OverflowError):
        return default
    if w < 1:
        w = 1
    return min(_MAX_HEADER_BAR, w)


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

    SEP_WIDTH = 70

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
    def color(cls, text: str, color_code: str) -> str:
        if not _colors_enabled():
            return text
        return f"{color_code}{text}{cls.RESET}"

    @classmethod
    def rule_heavy(cls) -> str:
        """Full-width strong separator (section boundaries in operator debug output)."""
        return cls.color("=" * cls.SEP_WIDTH, cls.DIM)

    @classmethod
    def rule_light(cls) -> str:
        """Full-width light separator."""
        return cls.color("-" * cls.SEP_WIDTH, cls.DIM)

    @classmethod
    def highlight_decision(cls, mode: str) -> str:
        """
        Color known decision-mode labels from the kernel. Unknown / empty labels
        are still shown (default emphasis); whitespace-only or unusable input → dim ``?``.
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
        title: str,
        *,
        width: int | float | str | None = 70,
    ) -> str:
        """Primary section block (demo summaries, operator debug). *width* via :func:`_clamped_header_bar_width`."""
        w = _clamped_header_bar_width(width, default=cls.SEP_WIDTH)
        bar = cls.color("═" * w, cls.DIM)
        line = f"  {cls.color(title.strip(), cls.B_CYAN + cls.BOLD)}"
        return f"\n{bar}\n{line}\n{bar}"

    @classmethod
    def subheader(cls, title: str) -> str:
        """Secondary section line under a header."""
        prefix = cls.color("▸", cls.DIM)
        label = cls.color(title.strip(), cls.CYAN + cls.BOLD)
        return f"\n  {prefix} {label}"
