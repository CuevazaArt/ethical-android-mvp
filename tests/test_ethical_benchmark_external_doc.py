"""ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md stays present and states non-circularity."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "proposals" / "ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md"


def test_external_validation_doc_exists_and_covers_circularity():
    text = DOC.read_text(encoding="utf-8")
    assert "circular" in text.lower() or "non-circularity" in text.lower()
    assert "expert" in text.lower()
    assert "run_empirical_pilot" in text or "empirical pilot" in text.lower()
