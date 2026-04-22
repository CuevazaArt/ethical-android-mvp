"""Tests for LAN governance replay sidecar builder and verify CLI (DJ-BL-15)."""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.lan_governance_replay_sidecar import (
    LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1,
    build_replay_sidecar_v1,
    fingerprint_event_conflicts_only,
    fingerprint_replay_sidecar,
)


def test_build_sidecar_and_fingerprint_stable() -> None:
    lg = {
        "integrity_batch": {
            "event_conflicts": [{"kind": "same_turn", "event_id": "x"}],
            "merge_context_echo": {"frontier_turn": 1},
        },
        "coordinator": {
            "aggregated_event_conflicts": [{"kind": "stale_event", "event_id": "y"}],
            "aggregated_frontier_witness_resolutions": [
                {
                    "source_batch": "integrity_batch",
                    "frontier_witness_resolution": {"advisory_max_observed_turn": 3},
                }
            ],
        },
    }
    s = build_replay_sidecar_v1(audit_ledger_fingerprint="abc", lan_governance=lg)
    assert s["schema"] == LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1
    assert s["audit_ledger_fingerprint"] == "abc"
    assert "integrity_batch" in s["batches"]
    fp1 = fingerprint_replay_sidecar(s)
    fp2 = fingerprint_replay_sidecar(s)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_fingerprint_event_conflicts_only() -> None:
    a = [{"kind": "same_turn", "event_id": "1"}]
    b = [{"kind": "same_turn", "event_id": "2"}]
    assert fingerprint_event_conflicts_only(a) == fingerprint_event_conflicts_only(a)
    assert fingerprint_event_conflicts_only(a) != fingerprint_event_conflicts_only(b)


def test_verify_sidecar_cli_prints_fingerprint() -> None:
    repo = Path(__file__).resolve().parents[1]
    script = repo / "scripts" / "eval" / "verify_lan_governance_replay_sidecar.py"
    sidecar = {
        "schema": LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1,
        "audit_ledger_fingerprint": "deadbeef",
    }
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(sidecar, f)
        path = f.name
    try:
        out = subprocess.run(
            [sys.executable, str(script), path],
            capture_output=True,
            text=True,
            check=True,
        )
        line = out.stdout.strip()
        assert len(line) == 64
    finally:
        os.unlink(path)
