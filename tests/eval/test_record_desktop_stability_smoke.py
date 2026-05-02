from __future__ import annotations

from scripts.eval.record_desktop_stability_smoke import run_stability_smoke


def test_run_stability_smoke_passes() -> None:
    passed, note = run_stability_smoke()

    assert passed is True
    assert "ping/status" in note.lower()
