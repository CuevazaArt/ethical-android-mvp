"""
Bayesian-style feedback updater for ethical **mixture weights** (ADR 0012 Level 2).

Uses **explicit** per-candidate ``(util, deon, virtue)`` scores (same linear mixture as
``dot(w, v)``) so Dirichlet sampling and winners can be evaluated **without numpy**.

When scenarios come from ``runner.ALL_SIMULATIONS`` with ``hypothesis_override`` on every
candidate, use :func:`scenario_candidate_triples_from_runner`. Otherwise keep using
``feedback_mixture_posterior`` (numpy + ``mixture_ranking``).

Optional **softmax likelihood** (Plackett-Luce): set ``KERNEL_FEEDBACK_LIKELIHOOD=softmax_is``
to use importance sampling + moment-matched Dirichlet projection from
:mod:`ethical_mixture_likelihood` instead of the default agreeing-sample heuristic.

Genome drift: clamps the **normalized** posterior mean to stay within ``max_drift`` of the
initial normalized prior per axis, then rescales to preserve total Dirichlet concentration.
"""
# Status: SCAFFOLD

from __future__ import annotations

import json
import logging
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.simulations.runner import ALL_SIMULATIONS

logger = logging.getLogger(__name__)

_DEFAULT_ALPHA = [3.0, 3.0, 3.0]


def _dirichlet_sample(alphas: list[float], n: int, rng: random.Random) -> list[list[float]]:
    """Draw *n* samples from Dirichlet(alphas) via Gamma ratios (pure Python)."""
    samples: list[list[float]] = []
    for _ in range(n):
        raw = [rng.gammavariate(a, 1.0) for a in alphas]
        total = sum(raw)
        samples.append([r / total for r in raw])
    return samples


def _mixed_score(candidate_scores: dict[str, float], weights: list[float]) -> float:
    return (
        weights[0] * candidate_scores["util"]
        + weights[1] * candidate_scores["deon"]
        + weights[2] * candidate_scores["virtue"]
    )


def _winner_at(
    candidates: dict[str, dict[str, float]],
    weights: list[float],
) -> tuple[str, float]:
    scored = {name: _mixed_score(c, weights) for name, c in candidates.items()}
    ranked = sorted(scored.items(), key=lambda x: -x[1])
    gap = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else ranked[0][1]
    return ranked[0][0], gap


def scenario_candidate_triples_from_runner(scenario_id: int) -> dict[str, dict[str, float]] | None:
    """
    Build ``{action_name: {util, deon, virtue}}`` from ``CandidateAction.hypothesis_override``.

    Returns ``None`` if any action lacks ``hypothesis_override``.
    """
    if scenario_id not in ALL_SIMULATIONS:
        return None
    scn = ALL_SIMULATIONS[scenario_id]()
    out: dict[str, dict[str, float]] = {}
    for a in scn.actions:
        if a.hypothesis_override is None:
            return None
        o = a.hypothesis_override
        out[a.name] = {"util": float(o[0]), "deon": float(o[1]), "virtue": float(o[2])}
    return out


def build_scenario_candidates_map(
    scenario_ids: list[int],
) -> dict[int, dict[str, dict[str, float]]] | None:
    """Return map for all IDs, or ``None`` if any scenario cannot supply explicit triples."""
    m: dict[int, dict[str, dict[str, float]]] = {}
    for sid in scenario_ids:
        t = scenario_candidate_triples_from_runner(sid)
        if t is None:
            return None
        m[sid] = t
    return m


@dataclass
class FeedbackItem:
    scenario_id: int
    preferred_action: str
    confidence: float = 1.0
    context_type: str | None = None
    timestamp: str | None = None


@dataclass
class FeedbackResult:
    posterior_alpha: list[float]
    posterior_mean: list[float]
    consistency: str
    p_all_satisfied: float
    per_scenario: dict[int, float]
    n_feedback_items: int
    log: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class BMAResult:
    win_probabilities: dict[str, float]
    alpha: list[float]
    n_samples: int


class FeedbackUpdater:
    """
    Maintains Dirichlet ``alpha`` over mixture weights; applies sequential feedback updates.

    Composes with :class:`WeightedEthicsScorer` by setting
    ``hypothesis_weights = posterior_mean()`` (normalized mean of ``alpha``).
    """

    def __init__(
        self,
        initial_alpha: list[float] | None = None,
        max_drift: float = 0.30,
        update_strength: float = 3.0,
        n_samples: int = 20_000,
        seed: int = 42,
    ):
        self.alpha = list(initial_alpha or _DEFAULT_ALPHA)
        self._initial_alpha = list(self.alpha)
        self.max_drift = max_drift
        self.update_strength = update_strength
        self.n_samples = n_samples
        self._seed = int(seed)
        self._rng = random.Random(seed)
        self._feedback_log: list[dict[str, Any]] = []

    def bma_win_probabilities(
        self,
        candidates: dict[str, dict[str, float]],
        n_samples: int | None = None,
    ) -> BMAResult:
        n = n_samples or self.n_samples
        samples = _dirichlet_sample(self.alpha, n, self._rng)
        wins: dict[str, int] = {name: 0 for name in candidates}
        for w in samples:
            winner, _ = _winner_at(candidates, w)
            wins[winner] = wins.get(winner, 0) + 1
        probs = {name: round(c / n, 6) for name, c in wins.items()}
        return BMAResult(win_probabilities=probs, alpha=list(self.alpha), n_samples=n)

    def update_from_feedback(
        self,
        feedback: FeedbackItem,
        candidates: dict[str, dict[str, float]],
    ) -> dict[str, Any]:
        samples = _dirichlet_sample(self.alpha, self.n_samples, self._rng)
        agreeing = [w for w in samples if _winner_at(candidates, w)[0] == feedback.preferred_action]

        if not agreeing:
            entry: dict[str, Any] = {
                "scenario_id": feedback.scenario_id,
                "preferred": feedback.preferred_action,
                "status": "infeasible",
                "p_preferred": 0.0,
            }
            self._feedback_log.append(entry)
            logger.warning(
                "Feedback infeasible: no sample makes '%s' win for scenario %d",
                feedback.preferred_action,
                feedback.scenario_id,
            )
            return entry

        p_preferred = len(agreeing) / len(samples)
        mean_agree = [sum(w[i] for w in agreeing) / len(agreeing) for i in range(3)]
        strength = self.update_strength * feedback.confidence
        new_alpha = [self.alpha[i] + strength * mean_agree[i] for i in range(3)]
        new_alpha = self._apply_drift_guard(new_alpha)
        self.alpha = new_alpha
        total = sum(self.alpha)
        normalized = [a / total for a in self.alpha]

        entry = {
            "scenario_id": feedback.scenario_id,
            "preferred": feedback.preferred_action,
            "status": "updated",
            "alpha": [round(a, 3) for a in self.alpha],
            "normalized": [round(n, 4) for n in normalized],
            "p_preferred": round(p_preferred, 4),
            "mean_agreeing_weights": [round(m, 4) for m in mean_agree],
        }
        self._feedback_log.append(entry)
        logger.info(
            "Feedback applied: scenario %d → '%s' α=%s P(pref)=%.3f",
            feedback.scenario_id,
            feedback.preferred_action,
            entry["alpha"],
            p_preferred,
        )
        return entry

    def check_consistency(
        self,
        feedbacks: list[FeedbackItem],
        scenario_candidates: dict[int, dict[str, dict[str, float]]],
    ) -> dict[str, Any]:
        samples = _dirichlet_sample(self.alpha, self.n_samples, self._rng)
        per_scenario_counts: dict[int, int] = {f.scenario_id: 0 for f in feedbacks}
        all_agree = 0
        n = len(samples)

        for w in samples:
            joint_ok = True
            for fb in feedbacks:
                cands = scenario_candidates[fb.scenario_id]
                winner, _ = _winner_at(cands, w)
                if winner == fb.preferred_action:
                    per_scenario_counts[fb.scenario_id] += 1
                else:
                    joint_ok = False
            if joint_ok:
                all_agree += 1

        p_all = all_agree / n
        per_scenario_marginal = {
            sid: round(per_scenario_counts[sid] / n, 4) for sid in per_scenario_counts
        }
        return {
            "consistency": "compatible" if p_all > 0.01 else "contradictory",
            "p_all_satisfied": round(p_all, 4),
            "per_scenario": per_scenario_marginal,
            "n_feedback_items": len(feedbacks),
        }

    def _use_softmax_likelihood_env(self) -> bool:
        m = os.environ.get("KERNEL_FEEDBACK_LIKELIHOOD", "").strip().lower()
        return m in ("softmax", "softmax_is", "plackett_luce", "1", "true", "yes", "on")

    def _ingest_feedback_softmax_is(
        self,
        feedbacks: list[FeedbackItem],
        scenario_candidates: dict[int, dict[str, dict[str, float]]],
    ) -> FeedbackResult:
        """ADR 0012 path: Plackett-Luce likelihood + iterated IS (see ``ethical_mixture_likelihood``)."""
        import numpy as np

        from src.modules.ethics.ethical_mixture_likelihood import (
            FeedbackObservation,
            sequential_posterior_update,
        )

        observations: list[FeedbackObservation] = []
        log: list[dict[str, Any]] = []
        for fb in feedbacks:
            cands = scenario_candidates.get(fb.scenario_id)
            if cands is None:
                log.append({"scenario_id": fb.scenario_id, "status": "unknown_scenario"})
                continue
            observations.append(
                FeedbackObservation(
                    scenario_id=fb.scenario_id,
                    preferred_action=fb.preferred_action,
                    candidates=cands,
                    confidence=fb.confidence,
                )
            )
        if not observations:
            total = sum(self.alpha)
            return FeedbackResult(
                posterior_alpha=[round(a, 3) for a in self.alpha],
                posterior_mean=[round(a / total, 4) for a in self.alpha],
                consistency="insufficient",
                p_all_satisfied=0.0,
                per_scenario={},
                n_feedback_items=len(feedbacks),
                log=log,
            )

        _beta_env = os.environ.get("KERNEL_FEEDBACK_SOFTMAX_BETA", "10.0").strip().lower()
        rng_np = np.random.default_rng(self._seed)
        alpha0 = np.asarray(self.alpha, dtype=np.float64)

        if _beta_env == "auto":
            from src.modules.ethics.ethical_mixture_likelihood import calibrate_beta

            _raw_grid = os.environ.get("KERNEL_FEEDBACK_BETA_GRID", "").strip()
            _grid: list[float] | None = (
                [float(x) for x in _raw_grid.replace(",", " ").split() if x]
                if _raw_grid
                else None  # use calibrate_beta default: [1,3,5,10,20,50]
            )
            _bias = float(os.environ.get("KERNEL_FEEDBACK_BETA_BIAS", "1.0"))
            beta, _cal_scores = calibrate_beta(
                observations,
                alpha0,
                beta_candidates=_grid,
                n_samples=min(self.n_samples, 5_000),  # lighter pass for calibration
                rng=np.random.default_rng(self._seed + 1),
                sensitivity_bias=_bias,
            )
            self._feedback_log.append(
                {
                    "event": "beta_calibration",
                    "selected_beta": beta,
                    "sensitivity_bias": _bias,
                    "grid_scores": _cal_scores,
                }
            )
        else:
            beta = float(_beta_env)

        final_alpha, seq_log = sequential_posterior_update(
            observations,
            alpha0,
            beta=beta,
            n_samples=self.n_samples,
            rng=rng_np,
            max_drift=self.max_drift,
        )
        self.alpha = [float(x) for x in final_alpha]
        self._feedback_log.extend(seq_log)

        known = [fb for fb in feedbacks if fb.scenario_id in scenario_candidates]
        if len(known) >= 2:
            consistency = self.check_consistency(known, scenario_candidates)
        else:
            consistency = {
                "consistency": "insufficient",
                "p_all_satisfied": 0.0,
                "per_scenario": {},
                "n_feedback_items": len(known),
            }

        total = sum(self.alpha)
        return FeedbackResult(
            posterior_alpha=[round(a, 3) for a in self.alpha],
            posterior_mean=[round(a / total, 4) for a in self.alpha],
            consistency=consistency["consistency"],
            p_all_satisfied=float(consistency["p_all_satisfied"]),
            per_scenario={int(k): float(v) for k, v in consistency.get("per_scenario", {}).items()},
            n_feedback_items=len(feedbacks),
            log=log + seq_log,
        )

    def ingest_feedback(
        self,
        feedbacks: list[FeedbackItem],
        scenario_candidates: dict[int, dict[str, dict[str, float]]],
        *,
        stop_on_infeasible: bool = True,
    ) -> FeedbackResult:
        if self._use_softmax_likelihood_env():
            return self._ingest_feedback_softmax_is(feedbacks, scenario_candidates)

        log: list[dict[str, Any]] = []
        for fb in feedbacks:
            cands = scenario_candidates.get(fb.scenario_id)
            if cands is None:
                log.append({"scenario_id": fb.scenario_id, "status": "unknown_scenario"})
                continue
            result = self.update_from_feedback(fb, cands)
            log.append(result)
            if stop_on_infeasible and result.get("status") == "infeasible":
                total = sum(self.alpha)
                return FeedbackResult(
                    posterior_alpha=[round(a, 3) for a in self.alpha],
                    posterior_mean=[round(a / total, 4) for a in self.alpha],
                    consistency="contradictory",
                    p_all_satisfied=0.0,
                    per_scenario={},
                    n_feedback_items=len(feedbacks),
                    log=log,
                )

        known = [fb for fb in feedbacks if fb.scenario_id in scenario_candidates]
        if len(known) >= 2:
            consistency = self.check_consistency(known, scenario_candidates)
        else:
            consistency = {
                "consistency": "insufficient",
                "p_all_satisfied": 0.0,
                "per_scenario": {},
                "n_feedback_items": len(known),
            }

        total = sum(self.alpha)
        return FeedbackResult(
            posterior_alpha=[round(a, 3) for a in self.alpha],
            posterior_mean=[round(a / total, 4) for a in self.alpha],
            consistency=consistency["consistency"],
            p_all_satisfied=float(consistency["p_all_satisfied"]),
            per_scenario={int(k): float(v) for k, v in consistency.get("per_scenario", {}).items()},
            n_feedback_items=len(feedbacks),
            log=log,
        )

    def posterior_mean(self) -> list[float]:
        total = sum(self.alpha)
        return [a / total for a in self.alpha]

    def posterior_concentration(self) -> float:
        return sum(self.alpha)

    def snapshot(self) -> dict[str, Any]:
        return {
            "alpha": list(self.alpha),
            "initial_alpha": list(self._initial_alpha),
            "max_drift": self.max_drift,
            "update_strength": self.update_strength,
            "n_samples": self.n_samples,
            "feedback_log": list(self._feedback_log),
        }

    @classmethod
    def restore(cls, data: dict[str, Any]) -> FeedbackUpdater:
        updater = cls(
            initial_alpha=data["initial_alpha"],
            max_drift=data["max_drift"],
            update_strength=data["update_strength"],
            n_samples=int(data.get("n_samples", 20_000)),
            seed=int(data.get("seed", 42)),
        )
        updater.alpha = list(data["alpha"])
        updater._seed = int(data.get("seed", 42))
        updater._feedback_log = list(data.get("feedback_log", []))
        return updater

    @staticmethod
    def load_feedback_file(path: str | Path) -> list[FeedbackItem]:
        raw_data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(raw_data, dict) and "items" in raw_data:
            raw_data = raw_data["items"]
        if not isinstance(raw_data, list):
            raise ValueError('feedback file must be a JSON list or {"items": [...]}')
        return [
            FeedbackItem(
                scenario_id=int(item["scenario_id"]),
                preferred_action=str(item["preferred_action"]),
                confidence=float(item.get("confidence", 1.0)),
                context_type=item.get("context_type"),
                timestamp=item.get("timestamp") if isinstance(item.get("timestamp"), str) else None,
            )
            for item in raw_data
        ]

    @classmethod
    def from_feedback_file(
        cls,
        path: str | Path,
        *,
        initial_alpha: list[float] | None = None,
        max_drift: float = 0.30,
        update_strength: float = 3.0,
        n_samples: int = 20_000,
        seed: int = 42,
    ) -> FeedbackUpdater:
        """Load JSON and return an updater; call :meth:`ingest_feedback` with scenario candidates."""
        _ = cls.load_feedback_file(path)
        return cls(
            initial_alpha=initial_alpha,
            max_drift=max_drift,
            update_strength=update_strength,
            n_samples=n_samples,
            seed=seed,
        )

    def _apply_drift_guard(self, new_alpha: list[float]) -> list[float]:
        """Clamp normalized posterior mean within ``max_drift`` of initial normalized prior."""
        total = sum(new_alpha)
        if total <= 0:
            return new_alpha
        conc = total
        norm_new = [a / total for a in new_alpha]
        total_init = sum(self._initial_alpha)
        norm_init = [a / total_init for a in self._initial_alpha]
        clamped_norm: list[float] = []
        for i in range(3):
            lo = norm_init[i] - self.max_drift
            hi = norm_init[i] + self.max_drift
            clamped_norm.append(min(hi, max(lo, norm_new[i])))
        s = sum(clamped_norm)
        renorm = [c / s for c in clamped_norm]
        return [r * conc for r in renorm]


def feedback_items_from_records(records: list[Any]) -> list[FeedbackItem]:
    """Convert ``FeedbackRecord``-like objects to :class:`FeedbackItem`."""
    out: list[FeedbackItem] = []
    for r in records:
        out.append(
            FeedbackItem(
                scenario_id=int(r.scenario_id),
                preferred_action=str(r.preferred_action),
                confidence=float(getattr(r, "confidence", 1.0)),
                context_type=getattr(r, "context_type", None),
                timestamp=getattr(r, "timestamp", None),
            )
        )
    return out
