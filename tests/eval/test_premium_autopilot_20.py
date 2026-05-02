from __future__ import annotations

from pathlib import Path

from scripts.eval.premium_autopilot_20 import (
    build_premium_prompts,
    execute_premium_autopilot,
)


def test_build_premium_prompts_has_20_unique_items() -> None:
    prompts = build_premium_prompts()
    assert len(prompts) == 20
    ids = {prompt.id for prompt in prompts}
    assert len(ids) == 20


def test_execute_premium_autopilot_generates_all_passed_report(tmp_path: Path) -> None:
    report = tmp_path / "premium-report.json"
    payload = execute_premium_autopilot(write_report=report)
    assert payload["total_prompts"] == 20
    assert payload["passed_prompts"] == 20
    assert payload["failed_prompts"] == 0
    assert payload["all_passed"] is True
    assert report.exists()
