"""ADR 0012 Level 3 — context-dependent mixture posteriors (mixture_ranking path)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from src.kernel import EthicalKernel
from src.modules.feedback_mixture_posterior import (
    classify_mixture_context,
    context_level3_enabled,
    load_and_apply_feedback,
    load_feedback_records,
    pick_active_alpha_for_context,
)


def test_classify_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_ACTIVE_CONTEXT_TYPE", "forced_ctx")
    assert classify_mixture_context("[SIM 9] x", "ctx", {}) == "forced_ctx"


def test_classify_scenario_map(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_ACTIVE_CONTEXT_TYPE", raising=False)
    monkeypatch.setenv("KERNEL_CONTEXT_SCENARIO_MAP_JSON", '{"3":"medical","7":"other"}')
    assert classify_mixture_context("[SIM 3] triage", "ctx", {}) == "medical"
    assert classify_mixture_context("[SIM 7] z", "ctx", {}) == "other"


def test_classify_keywords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_ACTIVE_CONTEXT_TYPE", raising=False)
    monkeypatch.delenv("KERNEL_CONTEXT_SCENARIO_MAP_JSON", raising=False)
    monkeypatch.setenv(
        "KERNEL_CONTEXT_KEYWORDS_JSON",
        json.dumps({"urgent": ["emergency"], "calm": ["walk"]}),
    )
    assert classify_mixture_context("walk the dog", "park", {}) == "calm"
    assert classify_mixture_context("medical emergency room", "x", {}) == "urgent"


def test_pick_active_alpha_prefers_key() -> None:
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    p = {"k1": a, "_global": b}
    assert np.allclose(pick_active_alpha_for_context(p, "k1"), a)
    assert np.allclose(pick_active_alpha_for_context(p, "missing"), b)


def test_level3_blended_mean_without_tick_context(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KERNEL_BAYESIAN_CONTEXT_LEVEL3", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "400")
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps(
            [
                {
                    "scenario_id": 1,
                    "preferred_action": "pick_up_can",
                    "context_type": "a",
                },
                {
                    "scenario_id": 1,
                    "preferred_action": "pick_up_can",
                    "context_type": "b",
                },
            ]
        ),
        encoding="utf-8",
    )
    rng = np.random.default_rng(0)
    alpha, status, meta = load_and_apply_feedback(p, rng=rng, tick_context=None)
    assert status == "compatible"
    assert meta.get("active_context_key") == "blended_mean"
    assert meta.get("updater") == "mixture_ranking_context_level3"
    assert np.sum(alpha) > 0


def test_kernel_sets_mixture_context_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KERNEL_BAYESIAN_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_BAYESIAN_CONTEXT_LEVEL3", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "500")
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps(
            [
                {
                    "scenario_id": 1,
                    "preferred_action": "pick_up_can",
                    "context_type": "bucket_a",
                },
                {
                    "scenario_id": 2,
                    "preferred_action": "calm_narrative",
                    "context_type": "bucket_b",
                },
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(p))
    monkeypatch.setenv(
        "KERNEL_CONTEXT_SCENARIO_MAP_JSON",
        json.dumps({"1": "bucket_a", "2": "bucket_b"}),
    )
    k = EthicalKernel(variability=False, seed=42, llm_mode="local")
    scn = __import__("src.simulations.runner", fromlist=["ALL_SIMULATIONS"]).ALL_SIMULATIONS[1]()
    d = k.process(
        scenario=f"[SIM 1] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=list(scn.actions),
    )
    assert d.mixture_context_key == "bucket_a"
    assert d.mixture_posterior_alpha is not None


def test_context_level3_disabled_skips_bucket_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("KERNEL_BAYESIAN_CONTEXT_LEVEL3", raising=False)
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "400")
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps(
            [
                {
                    "scenario_id": 1,
                    "preferred_action": "pick_up_can",
                    "context_type": "a",
                },
            ]
        ),
        encoding="utf-8",
    )
    rng = np.random.default_rng(1)
    _, _, meta = load_and_apply_feedback(p, rng=rng, tick_context=("x", "y", {}))
    assert meta.get("updater") == "mixture_ranking"
    assert "context_posteriors" not in meta


def test_records_roundtrip_context_type(tmp_path: Path) -> None:
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps([{"scenario_id": 1, "preferred_action": "pick_up_can", "context_type": "z"}]),
        encoding="utf-8",
    )
    recs = load_feedback_records(p)
    assert len(recs) == 1
    assert recs[0].context_type == "z"


def test_context_level3_enabled_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_BAYESIAN_CONTEXT_LEVEL3", "1")
    assert context_level3_enabled() is True
    monkeypatch.setenv("KERNEL_BAYESIAN_CONTEXT_LEVEL3", "0")
    assert context_level3_enabled() is False
