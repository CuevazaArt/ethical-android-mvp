"""Committed deploy helpers (Grafana JSON, etc.) stay valid."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_grafana_dashboard_json_parses():
    p = ROOT / "deploy" / "grafana" / "ethos-kernel-overview.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("title")
    assert data.get("uid") == "ethos-kernel-overview"
    assert isinstance(data.get("panels"), list)
    assert len(data["panels"]) >= 1
