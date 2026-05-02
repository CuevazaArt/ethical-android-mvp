from __future__ import annotations

from pathlib import Path

from scripts.eval.run_gate_maintenance_checklist import maintenance_commands


def test_maintenance_commands_use_repo_paths() -> None:
    root = Path(__file__).resolve().parents[2]
    cmds = maintenance_commands()
    assert len(cmds) >= 3
    assert any("record_g3_daily_contract_run.py" in str(c) for c in cmds)
    assert any("g2_transition_guard.py" in str(c) for c in cmds)
    assert any("desktop_gate_runner.py" in str(c) for c in cmds)
    evidence = root / "docs" / "collaboration" / "evidence"
    flat = [str(part) for cmd in cmds for part in cmd]
    assert str(evidence / "G2_TRANSITION_READINESS.json") in flat
