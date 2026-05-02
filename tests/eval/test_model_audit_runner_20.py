from __future__ import annotations

from pathlib import Path

from scripts.eval.model_audit_runner_20 import build_prompts, run_audit


def test_model_audit_board_has_20_unique_prompts() -> None:
    prompts = build_prompts()
    assert len(prompts) == 20
    assert len({p.id for p in prompts}) == 20


def test_model_audit_runner_passes_and_writes_report(tmp_path: Path) -> None:
    report = tmp_path / "model-audit-20.json"
    payload = run_audit(report=report)
    assert payload["total_prompts"] == 20
    assert payload["all_passed"] is True
    assert payload["failed_prompts"] == 0
    assert report.exists()
