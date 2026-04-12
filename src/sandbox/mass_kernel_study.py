"""
Million-scale batch study — one reproducible ``EthicalKernel.process`` per integer index.

Each index ``i`` derives pole weights, mixture weights, and (optionally stratified) scenario_id
from ``base_seed`` without storing large weight arrays in memory.

See ``docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from src.kernel import EthicalKernel
from src.kernel_components import KernelComponentOverrides
from src.modules.ethical_poles import EthicalPoles
from src.simulations.runner import ALL_SIMULATIONS

from .weight_sweep import POLE_KEYS

# Bump when JSONL row shape or semantics change (plotting / analysis tools).
RECORD_SCHEMA_VERSION = 1


def load_reference_labels(fixture_path: Path) -> dict[int, str | None]:
    """Map batch scenario_id -> reference action label if present."""
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
    out: dict[int, str | None] = {}
    for entry in data.get("scenarios", []):
        if entry.get("harness", "batch") != "batch":
            continue
        sid_key = entry.get("batch_id", entry.get("id"))
        if sid_key is None:
            continue
        sid = int(sid_key)
        ref = entry.get("reference_action")
        if ref is None:
            ref = entry.get("expected_decision")
        out[sid] = ref
    return out


def load_tier_labels(fixture_path: Path) -> dict[int, str | None]:
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
    out: dict[int, str | None] = {}
    for entry in data.get("scenarios", []):
        if entry.get("harness", "batch") != "batch":
            continue
        sid_key = entry.get("batch_id", entry.get("id"))
        if sid_key is None:
            continue
        sid = int(sid_key)
        out[sid] = entry.get("difficulty_tier")
    return out


def stratified_scenario_ids(n: int, *, seed: int) -> np.ndarray:
    """Length ``n`` array of scenario IDs in 1..9 — balanced counts (±1), then shuffled."""
    base = (np.arange(n, dtype=np.int64) % 9) + 1
    rng = np.random.default_rng(seed ^ 0x9E3779B9)
    rng.shuffle(base)
    return base


def _rng_for_index(i: int, base_seed: int) -> np.random.Generator:
    # Deterministic per index; independent of parallel scheduling order.
    s = (int(base_seed) + int(i)) * 100003 + int(i) * 7919
    return np.random.default_rng(s & 0xFFFFFFFFFFFFFFFF)


def run_single_simulation(
    i: int,
    *,
    base_seed: int,
    refs: dict[int, str | None],
    tiers: dict[int, str | None],
    stratify_scenario: bool,
    scenario_id_override: int | None,
    n_total: int,
) -> dict[str, Any]:
    """
    Run one batch simulation for index ``i``.

    If ``stratify_scenario``, scenario_id comes from ``stratified_scenario_ids(n_total, seed=base_seed)[i]``.
    Otherwise uniform integer 1..9 from the index-local RNG.
    """
    rng = _rng_for_index(i, base_seed)
    pole_dict = {k: float(0.05 + 0.9 * rng.random()) for k in POLE_KEYS}
    mix = rng.dirichlet(np.ones(3))

    if scenario_id_override is not None:
        sid = int(scenario_id_override)
    elif stratify_scenario:
        strat = stratified_scenario_ids(n_total, seed=base_seed)
        sid = int(strat[i % n_total])
    else:
        sid = int(rng.integers(1, 10))

    if sid not in ALL_SIMULATIONS:
        raise ValueError(f"Invalid scenario_id {sid}")

    kernel = EthicalKernel(
        variability=False,
        seed=int(base_seed) + i,
        llm_mode="local",
        components=KernelComponentOverrides(poles=EthicalPoles(base_weights=pole_dict)),
    )
    mw = mix / mix.sum()
    kernel.bayesian.hypothesis_weights = mw

    scn = ALL_SIMULATIONS[sid]()
    decision = kernel.process(
        scenario=f"[SIM {sid}] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=scn.actions,
    )
    ref = refs.get(sid)
    agree = ref is None or decision.final_action == ref
    tier = tiers.get(sid)

    return {
        "i": i,
        "kernel_seed": int(base_seed) + i,
        "scenario_id": sid,
        "difficulty_tier": tier,
        "pole_compassionate": pole_dict["compassionate"],
        "pole_conservative": pole_dict["conservative"],
        "pole_optimistic": pole_dict["optimistic"],
        "mixture_util": float(mw[0]),
        "mixture_deon": float(mw[1]),
        "mixture_virtue": float(mw[2]),
        "final_action": decision.final_action,
        "decision_mode": decision.decision_mode,
        "reference_action": ref,
        "agree_reference": agree,
    }


__all__ = [
    "RECORD_SCHEMA_VERSION",
    "load_reference_labels",
    "load_tier_labels",
    "run_single_simulation",
    "stratified_scenario_ids",
]
