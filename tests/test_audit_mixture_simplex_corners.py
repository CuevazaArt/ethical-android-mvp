"""Smoke tests for scripts/audit_mixture_simplex_corners.py (Phase-1 simplex audit)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_mixture_simplex_corners import audit_scenario  # noqa: E402


def test_audit_scenario_structure() -> None:
    r = audit_scenario(1)
    assert r["scenario_id"] == 1
    assert "corners" in r
    for key in ("util_corner", "deon_corner", "virtue_corner", "uniform_center"):
        assert key in r["corners"]
        c = r["corners"][key]
        assert "winner" in c
        assert "ranking" in c
        assert c["winner"] == c["ranking"][0]["action"]
    assert r["winner_varies_across_corners"] is False


def test_audit_unknown_scenario_raises() -> None:
    with pytest.raises(ValueError, match="Unknown scenario_id"):
        audit_scenario(99999)
