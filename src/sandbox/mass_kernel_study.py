"""
Million-scale batch study — one reproducible ``EthicalKernel.process`` per integer index.

Each index ``i`` derives pole weights, mixture weights, and (optionally stratified) scenario_id
from ``base_seed`` without storing large weight arrays in memory.

See ``docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md``.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from src.kernel import EthicalKernel
from src.kernel_components import KernelComponentOverrides
from src.modules.ethical_poles import EthicalPoles
from src.sandbox.synthetic_stochastic import SyntheticStochasticConfig, perturb_scenario_signals
from src.simulations.runner import ALL_SIMULATIONS

from .weight_sweep import POLE_KEYS

RECORD_SCHEMA_VERSION = 5

DEFAULT_STRESS_SCENARIO_IDS: tuple[int, ...] = (2, 5, 8)

# Tight-score frontier vignettes (lanes D in v3/v4).
DEFAULT_BORDERLINE_SCENARIO_IDS: tuple[int, ...] = (10, 11, 12)

# Polemic + synthetic extreme (lane E in v4).
DEFAULT_POLEMIC_EXTREME_IDS: tuple[int, ...] = (13, 14, 15)

# Three **classic** batch IDs spread across stakes/domain (save compute vs rotating all 1–9).
DEFAULT_CLASSIC_ECONOMY_IDS: tuple[int, ...] = (1, 5, 7)

_EXPERIMENT_PROTOCOL_LEGACY = "legacy"
_EXPERIMENT_PROTOCOL_V2 = "v2"
_EXPERIMENT_PROTOCOL_V3 = "v3"
_EXPERIMENT_PROTOCOL_V4 = "v4"

LANE_NAMES_V2: tuple[str, ...] = ("A_mixture_focus", "B_stress_scenarios", "C_ablation")
LANE_NAMES_V3: tuple[str, ...] = (
    "A_mixture_focus",
    "B_stress_scenarios",
    "C_ablation",
    "D_borderline",
)
LANE_NAMES_V4: tuple[str, ...] = (
    "A_mixture_focus",
    "B_stress_scenarios",
    "C_ablation",
    "D_borderline",
    "E_polemic_extreme",
)


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


def stratified_scenario_ids(
    n: int,
    *,
    seed: int,
    ids: tuple[int, ...] | None = None,
) -> np.ndarray:
    """
    Balanced rotation through scenario IDs, then shuffled.

    Default ``ids is None``: classic IDs **1..9**. With ``ids`` set (e.g. economy triple), only
    those IDs are used — fewer ``process()`` calls per distinct classic vignette.
    """
    if ids:
        k = len(ids)
        base = np.array([ids[i % k] for i in range(n)], dtype=np.int64)
    else:
        base = (np.arange(n, dtype=np.int64) % 9) + 1
    rng = np.random.default_rng(seed ^ 0x9E3779B9)
    rng.shuffle(base)
    return base


def stratified_stress_scenario_ids(
    n: int, stress_ids: tuple[int, ...], *, seed: int
) -> np.ndarray:
    if not stress_ids:
        raise ValueError("stress_ids must be non-empty")
    k = len(stress_ids)
    arr = np.array([stress_ids[i % k] for i in range(n)], dtype=np.int64)
    rng = np.random.default_rng(seed ^ 0x5F3759DF)
    rng.shuffle(arr)
    return arr


def allocate_lane_counts_n(n_sims: int, split: tuple[float, ...]) -> tuple[int, ...]:
    if abs(sum(split) - 1.0) > 1e-5:
        raise ValueError("lane_split must sum to 1.0")
    k = len(split)
    raw = [n_sims * f for f in split]
    floors = [int(x) for x in raw]
    rem = n_sims - sum(floors)
    frac_order = sorted(range(k), key=lambda i: raw[i] - floors[i], reverse=True)
    for j in range(rem):
        floors[frac_order[j]] += 1
    return tuple(floors)


def allocate_lane_counts(n: int, split: tuple[float, float, float]) -> tuple[int, int, int]:
    t = allocate_lane_counts_n(n, split)
    return t[0], t[1], t[2]


def _lane_and_local_index(
    i: int,
    *,
    n_total: int,
    lane_split: tuple[float, ...],
    lane_names: tuple[str, ...],
) -> tuple[str, int, tuple[int, ...]]:
    counts = allocate_lane_counts_n(n_total, lane_split)
    if len(counts) != len(lane_names):
        raise ValueError("lane_split and lane_names length mismatch")
    cum = 0
    for idx, name in enumerate(lane_names):
        n_lane = counts[idx]
        if i < cum + n_lane:
            return name, i - cum, counts
        cum += n_lane
    raise RuntimeError("lane index out of range")


def _rng_for_index(i: int, base_seed: int) -> np.random.Generator:
    s = (int(base_seed) + int(i)) * 100003 + int(i) * 7919
    return np.random.default_rng(s & 0xFFFFFFFFFFFFFFFF)


def _uniform_pole_dict(
    rng: np.random.Generator, lo: float, hi: float
) -> dict[str, float]:
    """Independent Uniform(lo, hi) per pole axis (legacy / lanes C, D, E)."""
    span = float(hi) - float(lo)
    return {k: float(lo + span * rng.random()) for k in POLE_KEYS}


def _mixture_dirichlet_sample(rng: np.random.Generator, alpha: float) -> np.ndarray:
    """
    Symmetric Dirichlet on the 3-simplex. ``alpha=1`` recovers the historical uniform-on-simplex draw.
    Larger ``alpha`` concentrates mass near ``(1/3, 1/3, 1/3)`` (finer local exploration).
    """
    a = max(1e-9, float(alpha))
    return rng.dirichlet(np.ones(3, dtype=np.float64) * a)


def _mixture_entropy(mw: np.ndarray) -> float:
    p = np.clip(mw.astype(np.float64), 1e-15, 1.0)
    p = p / p.sum()
    return float(-(p * np.log(p)).sum())


def _dominant_hypothesis(mw: np.ndarray) -> str:
    labels = ("util", "deon", "virtue")
    return labels[int(np.argmax(mw))]


def _ei_margin_bin(margin: float | None, has_second: bool) -> str:
    if not has_second or margin is None:
        return "single_or_tight_pruned"
    if margin < 0.05:
        return "tight"
    if margin < 0.15:
        return "medium"
    return "wide"


@contextmanager
def _temporary_environ(updates: dict[str, str]) -> Iterator[None]:
    previous: dict[str, str | None] = {k: os.environ.get(k) for k in updates}
    try:
        for k, v in updates.items():
            os.environ[k] = v
        yield
    finally:
        for k, old in previous.items():
            if old is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = old


def _ablation_spec(local_idx: int) -> tuple[str, dict[str, str]]:
    mode = local_idx % 4
    tags = (
        "baseline",
        "empirical_weights",
        "temporal_prior",
        "empirical_and_temporal",
    )
    envs: tuple[dict[str, str], ...] = (
        {},
        {"KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS": "1"},
        {"KERNEL_TEMPORAL_HORIZON_PRIOR": "1"},
        {
            "KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS": "1",
            "KERNEL_TEMPORAL_HORIZON_PRIOR": "1",
        },
    )
    return tags[mode], envs[mode]


def run_single_simulation(
    i: int,
    *,
    base_seed: int,
    refs: dict[int, str | None],
    tiers: dict[int, str | None],
    stratify_scenario: bool,
    scenario_id_override: int | None,
    n_total: int,
    experiment_protocol: str = _EXPERIMENT_PROTOCOL_LEGACY,
    lane_split: tuple[float, ...] = (0.45, 0.35, 0.2),
    stress_scenario_ids: tuple[int, ...] = DEFAULT_STRESS_SCENARIO_IDS,
    borderline_scenario_ids: tuple[int, ...] = DEFAULT_BORDERLINE_SCENARIO_IDS,
    polemic_extreme_ids: tuple[int, ...] = DEFAULT_POLEMIC_EXTREME_IDS,
    classic_economy_ids: tuple[int, ...] = DEFAULT_CLASSIC_ECONOMY_IDS,
    classic_stratify_economy: bool = False,
    poles_pre_argmax: bool = False,
    context_richness_pre_argmax: bool = False,
    signal_stress: float = 0.0,
    pole_weight_low: float = 0.05,
    pole_weight_high: float = 0.95,
    mixture_dirichlet_alpha: float = 1.0,
) -> dict[str, Any]:
    rng = _rng_for_index(i, base_seed)
    p_lo = float(np.clip(pole_weight_low, 0.0, 1.0))
    p_hi = float(np.clip(pole_weight_high, 0.0, 1.0))
    if p_lo >= p_hi:
        raise ValueError(f"pole_weight_low must be < pole_weight_high (got {p_lo}, {p_hi})")
    mix_alpha = max(1e-9, float(mixture_dirichlet_alpha))
    protocol = str(experiment_protocol).strip().lower()
    if protocol not in (
        _EXPERIMENT_PROTOCOL_LEGACY,
        _EXPERIMENT_PROTOCOL_V2,
        _EXPERIMENT_PROTOCOL_V3,
        _EXPERIMENT_PROTOCOL_V4,
    ):
        raise ValueError(f"Unknown experiment_protocol: {experiment_protocol!r}")

    ablation_tag = ""
    env_updates: dict[str, str] = {}

    v3 = protocol == _EXPERIMENT_PROTOCOL_V3
    v4 = protocol == _EXPERIMENT_PROTOCOL_V4

    if protocol == _EXPERIMENT_PROTOCOL_LEGACY:
        experiment_lane = "legacy_uniform"
        pole_dict = _uniform_pole_dict(rng, p_lo, p_hi)
        mix = _mixture_dirichlet_sample(rng, mix_alpha)
        if scenario_id_override is not None:
            sid = int(scenario_id_override)
        elif stratify_scenario:
            ids = classic_economy_ids if classic_stratify_economy else None
            strat = stratified_scenario_ids(n_total, seed=base_seed, ids=ids)
            sid = int(strat[i % n_total])
        else:
            sid = int(rng.integers(1, max(ALL_SIMULATIONS.keys()) + 1))
        poles_override = EthicalPoles(base_weights=pole_dict)

    else:
        names = LANE_NAMES_V4 if v4 else (LANE_NAMES_V3 if v3 else LANE_NAMES_V2)
        lane_name, local_i, _counts = _lane_and_local_index(
            i, n_total=n_total, lane_split=lane_split, lane_names=names
        )
        experiment_lane = lane_name
        mix = _mixture_dirichlet_sample(rng, mix_alpha)
        n_a, n_b, n_c = _counts[0], _counts[1], _counts[2]
        n_d = _counts[3] if len(_counts) >= 4 else 0
        n_e = _counts[4] if len(_counts) >= 5 else 0

        if lane_name == "A_mixture_focus":
            pole_dict = {k: float(EthicalPoles.BASE_WEIGHTS[k]) for k in POLE_KEYS}
            poles_override = EthicalPoles(base_weights=pole_dict)
            if scenario_id_override is not None:
                sid = int(scenario_id_override)
            elif stratify_scenario:
                strat_a = stratified_scenario_ids(
                    n_a, seed=base_seed ^ 0xA11EE, ids=classic_economy_ids
                )
                sid = int(strat_a[local_i % n_a])
            else:
                sid = int(rng.choice(np.array(classic_economy_ids, dtype=np.int64)))

        elif lane_name == "B_stress_scenarios":
            pole_dict = {k: float(EthicalPoles.BASE_WEIGHTS[k]) for k in POLE_KEYS}
            poles_override = EthicalPoles(base_weights=pole_dict)
            valid = tuple(s for s in stress_scenario_ids if s in ALL_SIMULATIONS)
            if not valid:
                raise ValueError(
                    f"No valid stress scenario IDs in {stress_scenario_ids!r} (ALL_SIMULATIONS keys)."
                )
            if scenario_id_override is not None:
                sid = int(scenario_id_override)
            elif stratify_scenario:
                strat_b = stratified_stress_scenario_ids(n_b, valid, seed=base_seed ^ 0xB22EE)
                sid = int(strat_b[local_i % n_b])
            else:
                sid = int(rng.choice(np.array(valid, dtype=np.int64)))

        elif lane_name == "C_ablation":
            pole_dict = _uniform_pole_dict(rng, p_lo, p_hi)
            poles_override = EthicalPoles(base_weights=pole_dict)
            ablation_tag, env_updates = _ablation_spec(local_i)
            if scenario_id_override is not None:
                sid = int(scenario_id_override)
            elif stratify_scenario:
                strat_c = stratified_scenario_ids(
                    n_c, seed=base_seed ^ 0xC33EE, ids=classic_economy_ids
                )
                sid = int(strat_c[local_i % n_c])
            else:
                sid = int(rng.choice(np.array(classic_economy_ids, dtype=np.int64)))

        elif lane_name == "D_borderline":
            pole_dict = _uniform_pole_dict(rng, p_lo, p_hi)
            poles_override = EthicalPoles(base_weights=pole_dict)
            valid = tuple(s for s in borderline_scenario_ids if s in ALL_SIMULATIONS)
            if not valid:
                raise ValueError(
                    f"No valid borderline scenario IDs in {borderline_scenario_ids!r}."
                )
            if scenario_id_override is not None:
                sid = int(scenario_id_override)
            elif stratify_scenario:
                strat_d = stratified_stress_scenario_ids(
                    n_d, valid, seed=base_seed ^ 0xD44EE
                )
                sid = int(strat_d[local_i % n_d])
            else:
                sid = int(rng.choice(np.array(valid, dtype=np.int64)))

        else:
            # E_polemic_extreme (v4)
            pole_dict = _uniform_pole_dict(rng, p_lo, p_hi)
            poles_override = EthicalPoles(base_weights=pole_dict)
            valid = tuple(s for s in polemic_extreme_ids if s in ALL_SIMULATIONS)
            if not valid:
                raise ValueError(f"No valid polemic IDs in {polemic_extreme_ids!r}.")
            if scenario_id_override is not None:
                sid = int(scenario_id_override)
            elif stratify_scenario:
                strat_e = stratified_stress_scenario_ids(
                    n_e, valid, seed=base_seed ^ 0xE55EE
                )
                sid = int(strat_e[local_i % n_e])
            else:
                sid = int(rng.choice(np.array(valid, dtype=np.int64)))

    if sid not in ALL_SIMULATIONS:
        raise ValueError(f"Invalid scenario_id {sid}")

    mw = mix / mix.sum()
    stress = float(np.clip(signal_stress, 0.0, 1.0))

    def _run_kernel() -> Any:
        kernel = EthicalKernel(
            variability=False,
            seed=int(base_seed) + i,
            llm_mode="local",
            components=KernelComponentOverrides(poles=poles_override),
        )
        kernel.bayesian.hypothesis_weights = mw
        scn = ALL_SIMULATIONS[sid]()
        signals_in = dict(scn.signals)
        noise_trace: dict[str, Any] | None = None
        if stress > 0.0:
            signals_in, noise_trace = perturb_scenario_signals(
                signals_in,
                rng,
                stress=stress,
                config=SyntheticStochasticConfig(),
            )
        decision = kernel.process(
            scenario=f"[SIM {sid}] {scn.name}",
            place=scn.place,
            signals=signals_in,
            context=scn.context,
            actions=scn.actions,
        )
        return decision, noise_trace

    merged_env = dict(env_updates)
    if poles_pre_argmax:
        merged_env["KERNEL_POLES_PRE_ARGMAX"] = "1"
    if context_richness_pre_argmax:
        merged_env["KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX"] = "1"

    if merged_env:
        with _temporary_environ(merged_env):
            decision, noise_trace = _run_kernel()
    else:
        decision, noise_trace = _run_kernel()

    br = decision.bayesian_result
    second_name = getattr(br, "second_action_name", None) if br else None
    second_ei = getattr(br, "second_expected_impact", None) if br else None
    ei_margin = getattr(br, "ei_margin", None) if br else None
    has_second = second_name is not None

    ref = refs.get(sid)
    agree = ref is None or decision.final_action == ref
    tier = tiers.get(sid)

    row: dict[str, Any] = {
        "i": i,
        "kernel_seed": int(base_seed) + i,
        "scenario_id": sid,
        "difficulty_tier": tier,
        "experiment_protocol": protocol,
        "experiment_lane": experiment_lane,
        "classic_economy_ids": list(classic_economy_ids),
        "poles_pre_argmax": bool(poles_pre_argmax),
        "context_richness_pre_argmax": bool(context_richness_pre_argmax),
        "signal_stress": round(stress, 6),
        "pole_compassionate": pole_dict["compassionate"],
        "pole_conservative": pole_dict["conservative"],
        "pole_optimistic": pole_dict["optimistic"],
        "mixture_util": float(mw[0]),
        "mixture_deon": float(mw[1]),
        "mixture_virtue": float(mw[2]),
        "mixture_entropy": round(_mixture_entropy(mw), 6),
        "dominant_hypothesis": _dominant_hypothesis(mw),
        "scorer_second_action": second_name,
        "scorer_second_ei": second_ei,
        "ei_margin": ei_margin,
        "ei_margin_bin": _ei_margin_bin(
            float(ei_margin) if ei_margin is not None else None, has_second
        ),
        "observation_palette": "",
        "final_action": decision.final_action,
        "decision_mode": decision.decision_mode,
        "reference_action": ref,
        "agree_reference": agree,
        "signal_noise_trace": noise_trace,
        "sampling_pole_lo": round(p_lo, 6),
        "sampling_pole_hi": round(p_hi, 6),
        "sampling_mixture_dirichlet_alpha": round(mix_alpha, 6),
    }
    if protocol != _EXPERIMENT_PROTOCOL_LEGACY:
        row["ablation_tag"] = ablation_tag if experiment_lane == "C_ablation" else ""
        row["stress_scenario_ids"] = list(stress_scenario_ids)
        row["borderline_scenario_ids"] = list(borderline_scenario_ids)
        row["polemic_extreme_ids"] = list(polemic_extreme_ids)
    else:
        row["ablation_tag"] = ""
        row["stress_scenario_ids"] = list(stress_scenario_ids) if stress_scenario_ids else []
        row["borderline_scenario_ids"] = list(borderline_scenario_ids)
        row["polemic_extreme_ids"] = list(polemic_extreme_ids)

    row["observation_palette"] = (
        f"{row['dominant_hypothesis']}|{row['ei_margin_bin']}|{row['experiment_lane']}"
    )

    return row


__all__ = [
    "DEFAULT_BORDERLINE_SCENARIO_IDS",
    "DEFAULT_CLASSIC_ECONOMY_IDS",
    "DEFAULT_POLEMIC_EXTREME_IDS",
    "DEFAULT_STRESS_SCENARIO_IDS",
    "LANE_NAMES_V2",
    "LANE_NAMES_V3",
    "LANE_NAMES_V4",
    "RECORD_SCHEMA_VERSION",
    "allocate_lane_counts",
    "allocate_lane_counts_n",
    "load_reference_labels",
    "load_tier_labels",
    "run_single_simulation",
    "stratified_scenario_ids",
    "stratified_stress_scenario_ids",
]
