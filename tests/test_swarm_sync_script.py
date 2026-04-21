"""CLI smoke tests for scripts/swarm_sync.py (V14 digest + local LLM mode snapshot)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_swarm_sync_dry_run_structure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.delenv("KERNEL_LLM_CLOUD_DISABLED", raising=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "swarm_sync.py"),
            "--dry-run",
            "--msg",
            "pytest handoff",
            "--block",
            "20.0",
            "--author",
            "test",
            "--ticket",
            "V14.0",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    line = proc.stdout.strip().splitlines()[-1]
    data = json.loads(line)
    assert data["msg"] == "pytest handoff"
    assert data["block"] == "20.0"
    assert data["llm_resolved_mode"] == "local"
    assert "v14" in data and "sha256_short" in data["v14"]
