"""Operator-facing ANSI helpers (Plan 8.1.2) / ``src.utils.terminal_colors``."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.terminal_colors import (
    _DEFAULT_SEP_WIDTH,
    _MAX_HEADER_BAR,
    Term,
    _clamped_header_bar_width,
    _enable_windows_ansi,
)


def test_default_sep_width_export_matches_base_class():
    """Module default bar width is public (8.1.27) — same integer as :attr:`Term.SEP_WIDTH` for the stock class."""
    assert isinstance(_DEFAULT_SEP_WIDTH, int)
    assert _DEFAULT_SEP_WIDTH >= 1
    assert _DEFAULT_SEP_WIDTH == Term.SEP_WIDTH


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
    h4 = Term.highlight_decision(None)
    assert "?" in h4


def test_subheader_coercion_matches_decision_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    """Plan 8.1.28 — :meth:`Term.subheader` accepts ``object`` like :meth:`highlight_decision`."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "1")
    s0 = Term.subheader(None)
    assert "?" in s0
    s1 = Term.subheader("  Section  ")
    assert "Section" in s1
    s2 = Term.subheader("   \t  ")
    assert "?" in s2
    s3 = Term.subheader(42)
    assert "42" in s3


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
    assert h3.count("═") == Term.SEP_WIDTH * 2
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


def test_clamped_header_bar_width_saturates_default_on_invalid_raw() -> None:
    """Oversized *default* must not win on bool/``None`` paths (Pragmatismo 8.1.27, defense in depth)."""
    assert _clamped_header_bar_width(True, default=9_999) == _MAX_HEADER_BAR
    assert _clamped_header_bar_width(None, default=9_999) == _MAX_HEADER_BAR


def test_rule_heavy_and_light_respect_clamped_width(monkeypatch) -> None:
    """``rule_heavy``/``rule_light`` optional *width* uses :func:`_clamped_header_bar_width` (Plan 8.1.19/22)."""
    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    assert Term.rule_heavy(width=9_999_999).count("=") == _MAX_HEADER_BAR
    assert Term.rule_light(width=12).count("-") == 12
    assert Term.rule_heavy().count("=") == Term.SEP_WIDTH


def test_rule_bars_clamp_when_subclass_sep_width_huge(monkeypatch: pytest.MonkeyPatch) -> None:
    """``rule_heavy`` / ``rule_light`` must not allocate beyond :data:`_MAX_HEADER_BAR` (Plan 8.1.19)."""

    class _Wide(Term):
        SEP_WIDTH = 9_999

    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    assert _Wide.rule_heavy().count("=") == _MAX_HEADER_BAR
    assert _Wide.rule_light().count("-") == _MAX_HEADER_BAR


def test_header_default_width_follows_subclass_sep_width(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default :meth:`Term.header` (no *width*) matches :meth:`_rule_width` / rules (Plan 8.1.22)."""

    class _Narrow(Term):
        SEP_WIDTH = 40

    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    h = _Narrow.header("Section")
    assert h.count("═") == 40 * 2
    assert _Narrow.rule_heavy().count("=") == 40


def test_header_invalid_width_fallback_uses_clamped_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """``width=True``/bad values use ``default=`` from :meth:`_rule_width`, not raw huge ``SEP_WIDTH`` (8.1.26)."""

    class _Wide(Term):
        SEP_WIDTH = 9_999

    monkeypatch.setenv("KERNEL_TERM_COLOR", "0")
    h = _Wide.header("C", width=True)  # type: ignore[arg-type]  # invalid width → default
    assert h.count("═") == _MAX_HEADER_BAR * 2
