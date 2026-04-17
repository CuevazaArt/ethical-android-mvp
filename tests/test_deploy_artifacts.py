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


def test_prometheus_alert_rules_reference_malabs_metrics():
    """Starter rules stay committed next to Grafana; operators load via Prometheus rule_files."""
    p = ROOT / "deploy" / "prometheus" / "ethos_kernel_alerts.yml"
    assert p.is_file()
    txt = p.read_text(encoding="utf-8")
    assert "ethos_kernel_malabs_blocks_total" in txt
    assert "ethos_kernel_perception_circuit_trips_total" in txt
    assert "EthosMalabsBlocksBurst" in txt
