"""V2.132: tests for the synthetic feedback ledger seed."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.seed_feedback_ledger import (
    GUIDED_ACTIONS,
    build_seed_events,
    summarize_seed,
    write_seed_jsonl,
)


def test_build_seed_events_is_deterministic_for_fixed_seed() -> None:
    a = build_seed_events(turns=50, seed=20260502)
    b = build_seed_events(turns=50, seed=20260502)
    assert a == b
    assert len(a) == 50


def test_build_seed_events_covers_every_guided_action() -> None:
    events = build_seed_events(turns=50, seed=42)
    seen = {e["action"] for e in events}
    assert seen == {a.name for a in GUIDED_ACTIONS}
    # Each event records valid signal + tagged source so it can be
    # filtered out of real-operator analysis.
    for event in events:
        assert event["signal"] in (1, -1)
        assert event["source"] == "synthetic_seed_v1"
        assert event["turn_id"].startswith("seed-")
        assert event["weights_at_time"] == [0.40, 0.35, 0.25]


def test_build_seed_events_rejects_zero_turns() -> None:
    import pytest

    with pytest.raises(ValueError):
        build_seed_events(turns=0, seed=1)


def test_summary_posterior_bias_is_capped() -> None:
    events = build_seed_events(turns=50, seed=20260502)
    summary = summarize_seed(events)
    biases = [a["posterior_bias"] for a in summary["actions"].values()]
    # Cap is +/-0.10 in src/core/feedback.py.
    for bias in biases:
        assert -0.10 - 1e-9 <= bias <= 0.10 + 1e-9
    # The seed is engineered to spread bias visibly across the cap range,
    # so we expect at least one strongly positive and one strongly
    # negative action — that's the demo signal an operator wants to see.
    assert max(biases) >= 0.05
    assert min(biases) <= -0.05


def test_write_seed_jsonl_round_trip(tmp_path: Path) -> None:
    events = build_seed_events(turns=10, seed=7)
    target = tmp_path / "seed.jsonl"
    write_seed_jsonl(events, target)
    lines = [
        json.loads(line)
        for line in target.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert lines == events
