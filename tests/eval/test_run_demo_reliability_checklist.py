from __future__ import annotations

from scripts.eval.run_demo_reliability_checklist import _default_checks


def test_default_demo_checklist_defines_10_checks() -> None:
    checks = _default_checks("python")
    assert len(checks) == 10
    assert checks[0].id == "A1"
    assert checks[-1].id == "T4"

