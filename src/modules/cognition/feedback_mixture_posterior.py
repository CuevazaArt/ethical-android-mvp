"""
Approximate Dirichlet posterior from operator feedback on batch scenarios — **Level 2** of ADR 0012.

**CLI:** ``scripts/run_feedback_posterior.py`` applies the same logic and prints JSON (optional
default path ``tests/fixtures/feedback/compatible_17_18_19.json``).

Uses mixture-only winners (same path as ``simplex_mixture_probe.mixture_ranking``) for listed
``scenario_id`` values. This is **not** exact conjugate inference; it is a pragmatic shift of
``α`` toward mixture samples consistent with stated preferences.

Env:

- ``KERNEL_BAYESIAN_FEEDBACK`` — enable loading and updating.
- ``KERNEL_FEEDBACK_PATH`` — JSON file (list of records).
- ``KERNEL_FEEDBACK_UPDATE_STRENGTH`` — default ``3.0``.
- ``KERNEL_FEEDBACK_MC_SAMPLES`` — inner MC size per feedback item (default 20000).

**Level 3 (context-dependent posteriors, mixture_ranking path only):**

- ``KERNEL_BAYESIAN_CONTEXT_LEVEL3`` — enable when feedback JSON rows include ``context_type``.
- ``KERNEL_ACTIVE_CONTEXT_TYPE`` — optional override for the current tick’s bucket key.
- ``KERNEL_CONTEXT_SCENARIO_MAP_JSON`` — optional ``{"1":"type_a","2":"type_b"}`` for ``[SIM n]`` in scenario text.
- ``KERNEL_CONTEXT_KEYWORDS_JSON`` — optional ``{"type_a":["word"],...}`` substring match on scenario+context.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from src.sandbox.simplex_mixture_probe import mixture_ranking
from src.simulations.runner import ALL_SIMULATIONS
from src.modules.cognition.bayesian_mixture_averaging import parse_bma_alpha_from_env
from src.modules.cognition.feedback_mixture_updater import (
    FeedbackUpdater,
    build_scenario_candidates_map,
    feedback_items_from_records,
)
from src.modules.ethics.weighted_ethics_scorer import WeightedEthicsScorer


@dataclass
class FeedbackRecord:
    scenario_id: int
    preferred_action: str
    confidence: float = 1.0
    timestamp: str | None = None
    context_type: str | None = None
    # Optional explicit action list — when present, _winner_at_mixture() uses these instead of
    # resolving via ALL_SIMULATIONS, enabling operation with dynamic or unknown scenario IDs.
    action_candidates: list[str] | None = None


def feedback_enabled() -> bool:
    return os.environ.get("KERNEL_BAYESIAN_FEEDBACK", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def feedback_update_strength() -> float:
    return float(os.environ.get("KERNEL_FEEDBACK_UPDATE_STRENGTH", "3.0"))


def feedback_mc_samples() -> int:
    return max(1000, int(os.environ.get("KERNEL_FEEDBACK_MC_SAMPLES", "20000")))


def context_level3_enabled() -> bool:
    """ADR 0012 Level 3 — per-``context_type`` Dirichlet posteriors (mixture_ranking path)."""
    return os.environ.get("KERNEL_BAYESIAN_CONTEXT_LEVEL3", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _feedback_has_context_types(records: list[FeedbackRecord]) -> bool:
    return any((r.context_type or "").strip() for r in records)


def classify_mixture_context(
    scenario: str,
    context: str,
    signals: dict[str, Any] | None,
) -> str:
    """
    Map the current tick to a string key aligned with ``FeedbackRecord.context_type``.

    Priority: ``KERNEL_ACTIVE_CONTEXT_TYPE`` → ``KERNEL_CONTEXT_SCENARIO_MAP_JSON`` (``[SIM n]`` in
    ``scenario``) → ``KERNEL_CONTEXT_KEYWORDS_JSON`` substring match on ``scenario`` + ``context``
    → ``default``.
    """
    override = os.environ.get("KERNEL_ACTIVE_CONTEXT_TYPE", "").strip()
    if override:
        return override
    m = re.search(r"\[SIM\s+(\d+)\]", scenario, re.IGNORECASE)
    if m:
        sid = m.group(1)
        raw = os.environ.get("KERNEL_CONTEXT_SCENARIO_MAP_JSON", "").strip()
        if raw:
            try:
                mp = json.loads(raw)
            except json.JSONDecodeError:
                mp = {}
            if isinstance(mp, dict) and sid in mp:
                return str(mp[sid])
    raw_kw = os.environ.get("KERNEL_CONTEXT_KEYWORDS_JSON", "").strip()
    if raw_kw:
        try:
            kw_map = json.loads(raw_kw)
        except json.JSONDecodeError:
            kw_map = {}
        blob = f"{scenario} {context}".lower()
        if isinstance(kw_map, dict):
            for ctype in sorted(kw_map.keys()):
                words = kw_map[ctype]
                if not isinstance(words, list):
                    continue
                for w in words:
                    if isinstance(w, str) and w.lower() in blob:
                        return str(ctype)
    return "default"


def pick_active_alpha_for_context(
    posteriors: dict[str, np.ndarray],
    active_key: str,
) -> np.ndarray:
    """Choose Dirichlet α for this tick; fall back to ``_global``, then mean of buckets."""
    if active_key in posteriors:
        return np.asarray(posteriors[active_key], dtype=np.float64).copy()
    if "_global" in posteriors:
        return np.asarray(posteriors["_global"], dtype=np.float64).copy()
    if not posteriors:
        return parse_bma_alpha_from_env()
    return np.mean(
        np.stack([np.asarray(v, dtype=np.float64) for v in posteriors.values()], axis=0), axis=0
    )


def _load_and_apply_feedback_level3_mixture(
    records: list[FeedbackRecord],
    *,
    rng: np.random.Generator,
    tick_context: tuple[str, str, dict[str, Any] | None] | None,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    """
    Independent sequential α update per ``context_type`` bucket (from ``_global`` when missing).

    When ``tick_context`` is None (e.g. CLI), the active α is the **elementwise mean** of bucket
    posteriors (``active_context_key`` = ``blended_mean``).
    """
    alpha0 = parse_bma_alpha_from_env()
    n_inner = feedback_mc_samples()
    strength = feedback_update_strength()

    buckets: dict[str, list[FeedbackRecord]] = {}
    for r in records:
        key = (r.context_type or "").strip() or "_global"
        buckets.setdefault(key, []).append(r)

    posteriors: dict[str, np.ndarray] = {}
    combined: dict[str, Any] = {
        "updater": "mixture_ranking_context_level3",
        "n_feedback_items": len(records),
        "per_bucket": [],
    }

    for bkey in sorted(buckets.keys()):
        recs = buckets[bkey]
        alpha_new, status, meta = sequential_alpha_update(
            alpha0.copy(),
            recs,
            n_inner=n_inner,
            strength=strength,
            rng=rng,
        )
        posteriors[bkey] = alpha_new
        combined["per_bucket"].append({"bucket": bkey, "status": status, "detail": meta})
        if status == "contradictory":
            combined["context_posteriors"] = {k: v.tolist() for k, v in posteriors.items()}
            combined["active_context_key"] = bkey
            return alpha_new, "contradictory", combined

    if tick_context is None:
        alpha_use = np.mean(
            np.stack([np.asarray(v, dtype=np.float64) for v in posteriors.values()], axis=0),
            axis=0,
        )
        active_key = "blended_mean"
    else:
        scenario, ctx, sig = tick_context
        active_key = classify_mixture_context(scenario, ctx, sig)
        alpha_use = pick_active_alpha_for_context(posteriors, active_key)

    combined["context_posteriors"] = {k: v.tolist() for k, v in posteriors.items()}
    combined["active_context_key"] = active_key

    j_rate, _ = joint_satisfaction_monte_carlo(
        alpha_use, records, n_samples=min(50000, n_inner * 2), rng=rng
    )
    combined["joint_satisfaction_rate"] = round(float(j_rate), 6)
    if j_rate < 0.01:
        combined["note"] = (
            "Low joint satisfaction under posterior; preferences may be jointly tight."
        )
    return alpha_use, "compatible", combined


def _parse_iso_timestamp(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp string to an aware UTC datetime, or return None."""
    if not ts:
        return None
    try:
        # Python 3.11+ handles Z; for 3.9/3.10 replace Z manually
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, AttributeError):
        return None


def _apply_time_decay(
    records: list[FeedbackRecord],
    halflife_days: float,
    reference_date: datetime | None = None,
) -> list[FeedbackRecord]:
    """
    Attenuate each record's ``confidence`` by exponential decay based on age.

    ``confidence *= 2 ** (-age_days / halflife_days)``

    Records without a parseable ``timestamp`` are left unchanged (no penalty for
    missing metadata).  Records already at ``confidence <= 0`` are dropped.

    Parameters
    ----------
    halflife_days : float
        Confidence halves every this many days.  Set via
        ``KERNEL_FEEDBACK_DECAY_HALFLIFE`` (e.g. ``90``).
    reference_date : datetime or None
        "Today" for age computation.  Defaults to ``datetime.now(UTC)``.
    """
    if halflife_days <= 0:
        return records
    ref = reference_date or datetime.now(UTC)
    out: list[FeedbackRecord] = []
    for rec in records:
        dt = _parse_iso_timestamp(rec.timestamp or "")
        if dt is not None:
            age_days = max(0.0, (ref - dt).total_seconds() / 86400.0)
            new_conf = rec.confidence * math.pow(2.0, -age_days / halflife_days)
        else:
            new_conf = rec.confidence  # no timestamp — no penalty
        if new_conf > 1e-9:
            import dataclasses as _dc

            out.append(_dc.replace(rec, confidence=new_conf))
    return out


def load_feedback_records(path: Path) -> list[FeedbackRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        raise ValueError('feedback file must be a JSON list or {"items": [...]}')
    out: list[FeedbackRecord] = []
    for row in data:
        sid = int(row["scenario_id"])
        pref = str(row["preferred_action"])
        conf = float(row.get("confidence", 1.0))
        ts = row.get("timestamp")
        ct = row.get("context_type")
        raw_cands = row.get("action_candidates")
        cands: list[str] | None = (
            [str(a) for a in raw_cands] if isinstance(raw_cands, list) and raw_cands else None
        )
        out.append(
            FeedbackRecord(
                scenario_id=sid,
                preferred_action=pref,
                confidence=conf,
                timestamp=ts if isinstance(ts, str) else None,
                context_type=ct if isinstance(ct, str) else None,
                action_candidates=cands,
            )
        )
    return out


def _winner_at_mixture(
    scenario_id: int,
    w: np.ndarray,
    *,
    action_candidates: list[str] | None = None,
) -> str | None:
    """Evaluate which action wins under mixture weights *w*.

    When *action_candidates* is provided, those are used directly and the call
    does **not** touch ``ALL_SIMULATIONS``, enabling dynamic or production
    scenarios beyond the fixed simulation registry.  Falls back to
    ``ALL_SIMULATIONS`` when *action_candidates* is ``None``.
    """
    if action_candidates is not None:
        r = mixture_ranking(
            WeightedEthicsScorer(),
            mixture=w,
            scenario=f"[dynamic] scenario_id={scenario_id}",
            context="",
            signals={},
            actions=action_candidates,
        )
        return r.get("winner")

    # Fallback: resolve via fixed simulation registry (backward compat)
    if scenario_id not in ALL_SIMULATIONS:
        raise ValueError(
            f"Unknown scenario_id {scenario_id} and no action_candidates provided. "
            "Supply 'action_candidates' in the feedback record for dynamic scenarios."
        )
    scn = ALL_SIMULATIONS[scenario_id]()
    text = f"[SIM {scenario_id}] {scn.name}"
    r = mixture_ranking(
        WeightedEthicsScorer(),
        mixture=w,
        scenario=text,
        context=scn.context,
        signals=scn.signals,
        actions=list(scn.actions),
    )
    return r.get("winner")


def joint_satisfaction_monte_carlo(
    alpha: np.ndarray,
    records: list[FeedbackRecord],
    *,
    n_samples: int,
    rng: np.random.Generator,
) -> tuple[float, bool]:
    """
    Fraction of Dirichlet(alpha) samples where **all** preferred actions win simultaneously.
    Returns (rate, likely_empty) where likely_empty is True if rate is ~0.
    """
    alpha = np.asarray(alpha, dtype=np.float64)
    ok = 0
    for _ in range(n_samples):
        w = rng.dirichlet(alpha)
        if all(
            _winner_at_mixture(r.scenario_id, w, action_candidates=r.action_candidates)
            == r.preferred_action
            for r in records
        ):
            ok += 1
    rate = ok / float(n_samples)
    return rate, rate < (1.0 / max(n_samples, 2))


def sequential_alpha_update(
    alpha: np.ndarray,
    records: list[FeedbackRecord],
    *,
    n_inner: int,
    strength: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    """
    For each feedback record, sample ``w ~ Dirichlet(alpha)``, keep samples where the winner
    matches ``preferred_action``, and set ``alpha += strength * mean(agreeing)``.

    If no agreeing sample for an item, returns **contradictory** for that step.
    """
    alpha = np.asarray(alpha, dtype=np.float64).copy()
    meta: dict[str, Any] = {"per_item": []}

    for rec in records:
        agreeing: list[np.ndarray] = []
        for _ in range(n_inner):
            w = rng.dirichlet(alpha)
            win = _winner_at_mixture(rec.scenario_id, w, action_candidates=rec.action_candidates)
            if win == rec.preferred_action:
                agreeing.append(w)
        if not agreeing:
            meta["per_item"].append(
                {"scenario_id": rec.scenario_id, "status": "no_agreeing_sample"}
            )
            return alpha, "contradictory", meta
        mean_agree = np.mean(np.stack(agreeing, axis=0), axis=0)
        alpha = alpha + float(strength) * float(rec.confidence) * mean_agree
        meta["per_item"].append(
            {
                "scenario_id": rec.scenario_id,
                "status": "updated",
                "n_agreeing": len(agreeing),
            }
        )

    return alpha, "compatible", meta


def _posterior_predictive_check(
    alpha_posterior: np.ndarray,
    holdout_records: list[FeedbackRecord],
    cmap: dict[int, dict[str, dict[str, float]]],
    *,
    beta: float = 10.0,
    n_samples: int = 5_000,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """
    P7 — Diagnostic: compute posterior predictive accuracy on held-out records.

    For each held-out item, evaluate ``P(preferred | alpha_posterior, beta)`` via
    Monte Carlo.  Returns mean predictive probability and per-item breakdown.

    Only runs when ``KERNEL_FEEDBACK_POSTERIOR_CHECK=1`` and at least one
    held-out record has resolvable candidates in *cmap*.
    """
    from src.modules.ethics.ethical_mixture_likelihood import FeedbackObservation, posterior_predictive_probability

    per_item: list[dict[str, Any]] = []
    probs: list[float] = []

    for rec in holdout_records:
        cands = cmap.get(rec.scenario_id)
        if cands is None:
            per_item.append({"scenario_id": rec.scenario_id, "status": "no_candidates"})
            continue
        obs = FeedbackObservation(
            scenario_id=rec.scenario_id,
            preferred_action=rec.preferred_action,
            candidates=cands,
            confidence=rec.confidence,
        )
        p = posterior_predictive_probability(
            obs, alpha_posterior, beta=beta, n_samples=n_samples, rng=rng
        )
        probs.append(p)
        per_item.append(
            {
                "scenario_id": rec.scenario_id,
                "preferred_action": rec.preferred_action,
                "p_predictive": round(p, 4),
            }
        )

    return {
        "n_holdout": len(holdout_records),
        "n_evaluated": len(probs),
        "mean_predictive_probability": round(float(sum(probs) / len(probs)), 4) if probs else None,
        "per_item": per_item,
    }


def _load_and_apply_feedback_explicit_triples(
    records: list[FeedbackRecord],
    *,
    rng: np.random.Generator,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    """ADR 0012 path: pure-Python :class:`FeedbackUpdater` with explicit util/deon/virtue triples."""
    sids = sorted({r.scenario_id for r in records})
    cmap = build_scenario_candidates_map(sids)
    if cmap is None:
        raise RuntimeError("explicit triples path requires hypothesis_override on all candidates")

    # P7 — hold out last 20% when posterior predictive check is enabled
    _ppc_on = os.environ.get("KERNEL_FEEDBACK_POSTERIOR_CHECK", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    holdout: list[FeedbackRecord] = []
    train_records = records
    if _ppc_on and len(records) >= 5:
        split = max(1, len(records) * 4 // 5)
        train_records = records[:split]
        holdout = records[split:]

    alpha_list = parse_bma_alpha_from_env().tolist()
    strength = feedback_update_strength()
    n_inner = feedback_mc_samples()
    seed = int(os.environ.get("KERNEL_FEEDBACK_SEED", "42"))
    max_drift = float(os.environ.get("KERNEL_FEEDBACK_MAX_DRIFT", "0.30"))
    updater = FeedbackUpdater(
        initial_alpha=alpha_list,
        max_drift=max_drift,
        update_strength=strength,
        n_samples=n_inner,
        seed=seed,
    )
    items = feedback_items_from_records(train_records)
    fr = updater.ingest_feedback(items, cmap, stop_on_infeasible=True)
    alpha_new = np.asarray(updater.alpha, dtype=np.float64)
    meta: dict[str, Any] = {
        "updater": "explicit_triples",
        "likelihood": (os.environ.get("KERNEL_FEEDBACK_LIKELIHOOD", "").strip() or "heuristic"),
        "feedback_log": fr.log,
        "n_feedback_items": len(train_records),
    }

    if fr.consistency == "contradictory":
        meta["joint_satisfaction_rate"] = 0.0
        return alpha_new, "contradictory", meta

    j_rate, _ = joint_satisfaction_monte_carlo(
        alpha_new, train_records, n_samples=min(50000, n_inner * 2), rng=rng
    )
    meta["joint_satisfaction_rate"] = round(float(j_rate), 6)
    if j_rate < 0.01:
        meta["note"] = "Low joint satisfaction under posterior; preferences may be jointly tight."

    # P7 — posterior predictive check on holdout
    if _ppc_on and holdout:
        _ppc_beta = float(
            os.environ.get("KERNEL_FEEDBACK_SOFTMAX_BETA", "10.0").strip()
            if os.environ.get("KERNEL_FEEDBACK_SOFTMAX_BETA", "").strip().lower() != "auto"
            else "10.0"
        )
        meta["posterior_predictive_check"] = _posterior_predictive_check(
            alpha_new,
            holdout,
            cmap,
            beta=_ppc_beta,
            n_samples=3_000,
            rng=rng,
        )

    return alpha_new, fr.consistency if fr.consistency != "insufficient" else "compatible", meta


def load_and_apply_feedback(
    path: Path,
    *,
    rng: np.random.Generator,
    tick_context: tuple[str, str, dict[str, Any] | None] | None = None,
) -> tuple[np.ndarray, str, dict[str, Any]]:
    """
    Load feedback JSON, start from ``parse_bma_alpha_from_env()`` as prior, run sequential
    update, and compute joint satisfaction rate under final alpha.

    If every referenced scenario has ``hypothesis_override`` on all candidates (e.g. 17–19),
    uses :class:`FeedbackUpdater` (pure Python, explicit triples). Otherwise uses numpy +
    ``mixture_ranking`` (full scorer path).

    **Level 3 (ADR 0012):** When ``KERNEL_BAYESIAN_CONTEXT_LEVEL3`` is on and at least one
    feedback row has ``context_type``, the mixture_ranking path uses **independent** sequential
    updates per bucket and selects α for this tick via :func:`classify_mixture_context` when
    ``tick_context`` is ``(scenario, context, signals)``. Explicit-triples feedback still uses a
    **single** global posterior (see ``meta["level3_note"]``).

    Returns:
        ``(posterior_alpha, consistency, details)`` where consistency is
        ``compatible`` | ``contradictory`` | ``insufficient`` (empty file).
    """
    records = load_feedback_records(path)
    if not records:
        a = parse_bma_alpha_from_env()
        return a, "insufficient", {"reason": "empty_feedback"}

    # P5 — Temporal decay: attenuate confidence of old feedback
    _decay_str = os.environ.get("KERNEL_FEEDBACK_DECAY_HALFLIFE", "").strip()
    if _decay_str:
        try:
            _halflife = float(_decay_str)
            _n_before = len(records)
            records = _apply_time_decay(records, _halflife)
            if not records:
                a = parse_bma_alpha_from_env()
                return (
                    a,
                    "insufficient",
                    {
                        "reason": "all_records_decayed",
                        "halflife_days": _halflife,
                        "n_before_decay": _n_before,
                    },
                )
        except ValueError:
            pass  # malformed env var — proceed without decay

    sids = sorted({r.scenario_id for r in records})
    if build_scenario_candidates_map(sids) is not None:
        a, c, m = _load_and_apply_feedback_explicit_triples(records, rng=rng)
        if context_level3_enabled() and _feedback_has_context_types(records):
            m["level3"] = "explicit_triples_global_only"
            m["level3_note"] = (
                "KERNEL_BAYESIAN_CONTEXT_LEVEL3 is not applied per context when explicit "
                "hypothesis_override triples are used; posterior is global."
            )
        return a, c, m

    if context_level3_enabled() and _feedback_has_context_types(records):
        return _load_and_apply_feedback_level3_mixture(records, rng=rng, tick_context=tick_context)

    # P7 holdout split for mixture_ranking path
    _ppc_on = os.environ.get("KERNEL_FEEDBACK_POSTERIOR_CHECK", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    holdout_mr: list[FeedbackRecord] = []
    train_records_mr = records
    if _ppc_on and len(records) >= 5:
        split = max(1, len(records) * 4 // 5)
        train_records_mr = records[:split]
        holdout_mr = records[split:]

    alpha0 = parse_bma_alpha_from_env()
    n_inner = feedback_mc_samples()
    strength = feedback_update_strength()

    alpha_new, status, meta = sequential_alpha_update(
        alpha0,
        train_records_mr,
        n_inner=n_inner,
        strength=strength,
        rng=rng,
    )

    j_rate, _ = joint_satisfaction_monte_carlo(
        alpha_new, train_records_mr, n_samples=min(50000, n_inner * 2), rng=rng
    )
    meta["joint_satisfaction_rate"] = round(float(j_rate), 6)
    meta["n_feedback_items"] = len(train_records_mr)
    meta["updater"] = "mixture_ranking"

    if status == "contradictory":
        return alpha_new, "contradictory", meta

    if j_rate < 0.01:
        meta["note"] = "Low joint satisfaction under posterior; preferences may be jointly tight."

    # P7 — posterior predictive check: only for holdout records resolvable via ALL_SIMULATIONS
    if _ppc_on and holdout_mr:
        holdout_sids = sorted({r.scenario_id for r in holdout_mr})
        _ho_cmap = build_scenario_candidates_map(holdout_sids)
        if _ho_cmap:
            _ppc_beta = float(
                os.environ.get("KERNEL_FEEDBACK_SOFTMAX_BETA", "10.0")
                if os.environ.get("KERNEL_FEEDBACK_SOFTMAX_BETA", "").strip().lower() != "auto"
                else "10.0"
            )
            meta["posterior_predictive_check"] = _posterior_predictive_check(
                alpha_new,
                holdout_mr,
                _ho_cmap,
                beta=_ppc_beta,
                n_samples=3_000,
                rng=rng,
            )

    return alpha_new, "compatible", meta
