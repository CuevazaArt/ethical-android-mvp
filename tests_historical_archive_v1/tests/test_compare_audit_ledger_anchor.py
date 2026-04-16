"""CLI test for compare_audit_ledger_anchor (Phase 3 stub)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from src.modules.mock_dao_audit_replay import fingerprint_audit_ledger

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "eval" / "compare_audit_ledger_anchor.py"


@pytest.mark.skipif(not SCRIPT.is_file(), reason="anchor script missing")
def test_compare_audit_ledger_anchor_cli_match(tmp_path: Path) -> None:
    rows: list[dict] = []
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    fp = fingerprint_audit_ledger(rows)

    out = subprocess.run(
        [sys.executable, str(SCRIPT), str(p), fp],
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0
    assert "match" in out.stdout
