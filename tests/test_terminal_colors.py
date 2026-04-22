"""Operator-facing ANSI helpers (Plan 8.1.2) / ``src.utils.terminal_colors``."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.terminal_colors import (
    _MAX_HEADER_BAR,
    _clamped_header_bar_width,
    Term,
    _enable_windows_ansi,
)


def test_header_subheader_plain_when_color_off(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    monkeypatch.delenv("NO_COLOR", raising=False)
    h = Term.header("Daily Summary Profile")
    assert "\033" not in h
    assert "Daily Summary Profile" in h
    s = Term.subheader("Psi Sleep Retrospective")
    assert "\033" not in s
    assert "Psi Sleep Retrospective" in s


def test_no_color_env_forces_plain_even_when_kernel_color_on(monkeypatch):
    """https://no-color.org/ — non-empty NO_COLOR wins for CI and pipes."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    monkeypatch.setenv("NO_COLOR", "1")
    assert "\033" not in Term.color("hello", Term.RED)
    assert Term.color("hello", Term.RED) == "hello"
    assert "\033" not in Term.header("Title")
    assert "Title" in Term.header("Title")


def test_header_subheader_use_escape_codes_when_color_on(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    h = Term.header("Block")
    assert "\033[" in h
    assert "Block" in h
    s = Term.subheader("Section")
    assert "\033[" in s
    assert "Section" in s


def test_color_respects_switch(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    assert Term.color("x", Term.RED) == "x"


def test_enable_windows_ansi_is_noop_off_windows():
    if sys.platform == "win32":
        pytest.skip("Windows-only branch")
    _enable_windows_ansi()


def test_highlight_decision_known_modes():
    assert "D_fast" in Term.highlight_decision("D_fast")
    assert "gray_zone" in Term.highlight_decision("gray_zone")


def test_highlight_decision_whitespace_trim_and_empty(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    h = Term.highlight_decision("  D_fast  ")
    assert "D_fast" in h
    h2 = Term.highlight_decision("")
    assert "?" in h2
    h3 = Term.highlight_decision("   \t  ")
    assert "?" in h3


def test_highlight_impact_brackets_float():
    assert "+0.000" in Term.highlight_impact(0.0)


def test_highlight_impact_nonfinite_dimmed():
    s_nan = Term.highlight_impact(float("nan"))
    assert "nan" in s_nan.lower() or "NAN" in s_nan
    s_inf = Term.highlight_impact(float("inf"))
    assert "inf" in s_inf.lower()


def test_highlight_impact_invalid_coercion_falls_back(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    out = Term.highlight_impact(object())
    assert "?" in out


def test_highlight_impact_overflow_in_float_protocol_falls_back(monkeypatch):
    """``float(x)`` may raise ``OverflowError`` (e.g. pathological ``__float__``)."""

    class _OverflowOnFloat:
        def __float__(self) -> float:
            raise OverflowError("huge")

    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    assert "?" in Term.highlight_impact(_OverflowOnFloat())


def test_header_bar_width_clamped_and_safe(monkeypatch):
    """Huge / invalid widths must not build multi-megabyte strings (Harden-In-Place)."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    h = Term.header("W", width=9_999_999)
    assert h.count("═") == _MAX_HEADER_BAR * 2
    h2 = Term.header("B", width=-5)
    assert h2.count("═") == 1 * 2
    h3 = Term.header("C", width=True)  # bool is a bad width
    assert h3.count("═") == 70 * 2
    h4 = Term.header("N", width=float("nan"))
    assert h4.count("═") == Term.SEP_WIDTH * 2


def test_header_bar_width_huge_int_does_not_use_float_of_int(monkeypatch):
    """``float(huge int)`` can be inf; bar width must still clamp (Pragmatismo V4.0)."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    w_int = 10**400
    h = Term.header("Big", width=w_int)
    assert h.count("═") == _MAX_HEADER_BAR * 2


def test_header_bar_width_accepts_numeric_str(monkeypatch):
    """Operator / env may pass width as a string; still finite-capped (Plan 8.1.14)."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    h = Term.header("S", width="  42  ")
    assert h.count("═") == 42 * 2


def test_header_bar_width_bad_str_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    h = Term.header("S", width="nope")
    assert h.count("═") == Term.SEP_WIDTH * 2


def test_clamped_header_bar_width_is_public_and_matches_header_logic() -> None:
    """``__all__`` exports the same coercions :meth:`Term.header` uses (Plan 8.1.18)."""
    assert _clamped_header_bar_width("  40  ", default=Term.SEP_WIDTH) == 40
    assert _clamped_header_bar_width(40, default=Term.SEP_WIDTH) == 40
    assert _clamped_header_bar_width(9_999, default=Term.SEP_WIDTH) == _MAX_HEADER_BAR
