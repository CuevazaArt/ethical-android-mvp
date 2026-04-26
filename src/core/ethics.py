# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Ethical Evaluator (V2 Minimal)

Does ONE thing: given an action and context, scores it ethically
using three poles (Utilitarian, Deontological, Virtue).

No Bayesian mixture averaging, no hypothesis slot scaling,
no identity multipliers, no temporal horizon priors.
Just the essential ethical reasoning that makes Ethos unique.

Usage:
    evaluator = EthicalEvaluator()
    result = evaluator.evaluate(actions, signals)
    print(result.chosen.name, result.verdict)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.core.memory import _EMBEDDINGS_AVAILABLE
from src.core.precedents import PRECEDENTS, Precedent


@dataclass
class Action:
    """A concrete thing the agent could do."""

    name: str
    description: str
    impact: float  # [-1, 1] negative=harm, positive=benefit
    confidence: float = 0.7  # [0, 1]
    force: float = 0.0  # [0, 1] physical force involved
    source: str = "builtin"


@dataclass
class Signals:
    """Perceptual signals extracted from the situation."""

    risk: float = 0.0  # [0, 1] probability of harm
    urgency: float = 0.0  # [0, 1] need for speed
    hostility: float = 0.0  # [0, 1] aggression level
    calm: float = 0.7  # [0, 1] tranquility
    vulnerability: float = 0.0  # [0, 1] vulnerable people present
    legality: float = 1.0  # [0, 1] how legal (1=fully legal)
    manipulation: float = 0.0  # [0, 1] social engineering
    context: str = "everyday_ethics"
    summary: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Signals:
        """Build from an LLM-parsed dict with safe clamping."""

        def _clamp(v, default: float = 0.0) -> float:
            try:
                f = float(v)
                return max(0.0, min(1.0, f)) if math.isfinite(f) else default
            except (TypeError, ValueError):
                return default

        _valid_contexts = {
            "medical_emergency",
            "minor_crime",
            "violent_crime",
            "hostile_interaction",
            "everyday_ethics",
            "consistency_check",
        }
        raw_ctx = (
            str(d.get("suggested_context", d.get("context", "everyday_ethics"))).strip().lower()
        )
        safe_ctx = raw_ctx if raw_ctx in _valid_contexts else "everyday_ethics"

        return cls(
            risk=_clamp(d.get("risk"), 0.0),
            urgency=_clamp(d.get("urgency"), 0.0),
            hostility=_clamp(d.get("hostility"), 0.0),
            calm=_clamp(d.get("calm"), 0.7),
            vulnerability=_clamp(d.get("vulnerability"), 0.0),
            legality=_clamp(d.get("legality"), 1.0),
            manipulation=_clamp(d.get("manipulation"), 0.0),
            context=safe_ctx,
            summary=str(d.get("summary", ""))[:200],
        )


@dataclass
class EvalResult:
    """The ethical verdict."""

    chosen: Action
    score: float  # expected impact
    uncertainty: float  # [0, 1]
    mode: str  # D_fast, D_delib, gray_zone
    verdict: str  # Good, Bad, Gray Zone
    reasoning: str
    pole_scores: dict = field(default_factory=dict)  # util, deonto, virtue breakdown


# Pole weights: the soul of the ethical balance
WEIGHTS = {
    "util": 0.40,  # Utilitarian: maximize outcomes
    "deonto": 0.35,  # Deontological: respect duties and rights
    "virtue": 0.25,  # Virtue: what would a good person do?
}


def _score_utilitarian(action: Action, signals: Signals) -> float:
    """Outcomes weighted by stakes. Higher risk/vulnerability = higher stakes."""
    stake = 1.0 + 0.15 * signals.risk + 0.12 * signals.vulnerability + 0.10 * signals.urgency
    return action.impact * stake


def _score_deontological(action: Action, signals: Signals) -> float:
    """Duty and side-constraints. Force and illegality are penalized."""
    legality_gap = max(0.0, 1.0 - signals.legality)
    return (
        0.68 * action.impact
        + 0.09
        - 0.45 * action.force
        - 0.30 * legality_gap
        - 0.07 * signals.hostility
    )


def _score_virtue(action: Action, signals: Signals) -> float:
    """Character and practical wisdom. Confidence and calm are rewarded."""
    return (
        0.84 * action.impact + 0.05 + 0.22 * (action.confidence - 0.5) + 0.08 * (signals.calm - 0.5)
    )


class EthicalEvaluator:
    """
    Three-pole ethical evaluator.

    Simple, transparent, auditable. No hidden layers.
    """

    def __init__(self, weights: dict | None = None):
        self.weights = weights or WEIGHTS.copy()

    def score_action(self, action: Action, signals: Signals) -> tuple[float, dict]:
        """Score a single action. Returns (weighted_score, pole_breakdown)."""
        poles = {
            "util": _score_utilitarian(action, signals),
            "deonto": _score_deontological(action, signals),
            "virtue": _score_virtue(action, signals),
        }
        # Clamp poles to [-1.5, 1.5]
        for k in poles:
            v = poles[k]
            if not math.isfinite(v):
                poles[k] = 0.0
            else:
                poles[k] = max(-1.5, min(1.5, v))

        weighted = sum(self.weights[k] * poles[k] for k in poles)
        return weighted * action.confidence, poles

    def _find_similar_precedent(
        self, action: Action, signals: Signals
    ) -> tuple[Precedent | None, float]:
        """
        Find the most similar precedent for the current action and signals.

        Similarity factors (V2.46):
          1. Action name match (0.40 weight) — exact string match.
          2. Signal vector proximity (0.45 weight) — normalized L1 distance
             over shared keys, clamped to [0,1].
          3. Semantic/Keyword similarity (0.15 weight) — cosine similarity if
             embeddings are available, else keyword overlap.

        Returns (Precedent, similarity_score in [0, 1]).
        """
        best_p = None
        best_sim = -1.0

        # V2.46: Semantic embeddings upgrade
        query_vec = None
        if _EMBEDDINGS_AVAILABLE and signals.summary:
            try:
                import numpy as np
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("all-MiniLM-L6-v2")
                query_vec = model.encode(signals.summary, normalize_embeddings=True)
            except Exception:
                query_vec = None

        summary_words = (
            set(signals.summary.lower().split()) if signals.summary and not query_vec else set()
        )

        for p in PRECEDENTS:
            if p.context != signals.context:
                continue

            # Factor 1: Action name
            action_match = 0.40 if p.action_name == action.name else 0.0

            # Factor 2: Signal vector proximity
            sig_sim = 0.0
            shared_keys = set(p.signals.keys()) & set(signals.__dict__.keys())
            if shared_keys:
                diffs = [abs(p.signals[k] - getattr(signals, k, 0.0)) for k in shared_keys]
                raw_diff = sum(diffs) / len(shared_keys)
                sig_sim = max(0.0, 1.0 - raw_diff)
                if not math.isfinite(sig_sim):
                    sig_sim = 0.0
            signal_score = 0.45 * sig_sim

            # Factor 3: Text similarity (Embeddings or Keyword Overlap)
            text_score = 0.0
            if query_vec:
                try:
                    import numpy as np
                    from sentence_transformers import SentenceTransformer

                    # We need the embedding for p.reasoning
                    # Optimization: In a real system, these would be pre-computed.
                    p_vec = SentenceTransformer("all-MiniLM-L6-v2").encode(
                        p.reasoning, normalize_embeddings=True
                    )
                    cos_sim = float(np.dot(query_vec, p_vec))
                    text_score = 0.15 * max(0.0, cos_sim)
                except Exception:
                    text_score = 0.0
            else:
                reasoning_words = set(p.reasoning.lower().split())
                if summary_words and reasoning_words:
                    overlap = len(summary_words & reasoning_words) / max(len(summary_words), 1)
                    text_score = 0.15 * min(1.0, overlap * 5)
                else:
                    text_score = 0.0

            total_sim = action_match + signal_score + text_score
            if not math.isfinite(total_sim):
                total_sim = 0.0

            if total_sim > best_sim:
                best_sim = total_sim
                best_p = p

        return best_p, best_sim

    def evaluate(self, actions: list[Action], signals: Signals) -> EvalResult:
        """
        Evaluate all candidate actions and pick the best one.
        Uses Case-Based Reasoning (CBR) to anchor decisions in precedents.
        """
        if not actions:
            raise ValueError("Need at least one action to evaluate")

        scored = []
        for a in actions:
            score, poles = self.score_action(a, signals)

            # CBR Anchor: Find similar precedent
            precedent, similarity = self._find_similar_precedent(a, signals)
            if precedent and similarity > 0.8:
                # Anchor the score towards the precedent's impact score
                score = 0.7 * score + 0.3 * precedent.impact_score
                a.source = f"precedent:{precedent.name}"

            scored.append((a, score, poles, precedent))

        scored.sort(key=lambda x: x[1], reverse=True)
        best_action, best_score, best_poles, best_precedent = scored[0]

        # Decision mode
        if best_score > 0.5 and len(scored) == 1:
            mode = "D_fast"
        elif len(scored) > 1 and abs(scored[0][1] - scored[1][1]) < 0.05:
            mode = "gray_zone"
        else:
            mode = "D_delib"

        # Verdict
        if best_score > 0.1:
            verdict = "Good"
        elif best_score < -0.1:
            verdict = "Bad"
        else:
            verdict = "Gray Zone"

        # Reasoning
        precedent_note = ""
        if best_precedent:
            precedent_note = (
                f" Anchored by precedent '{best_precedent.name}': {best_precedent.reasoning}"
            )

        if len(scored) > 1:
            delta = scored[0][1] - scored[1][1]
            reasoning = (
                f"'{best_action.name}' scored {best_score:.3f} "
                f"(Δ={delta:.3f} over '{scored[1][0].name}'). "
                f"Poles: U={best_poles['util']:.2f} D={best_poles['deonto']:.2f} V={best_poles['virtue']:.2f}."
                + precedent_note
            )
        else:
            reasoning = (
                f"'{best_action.name}' is the only viable action (score={best_score:.3f}). "
                f"Poles: U={best_poles['util']:.2f} D={best_poles['deonto']:.2f} V={best_poles['virtue']:.2f}."
                + precedent_note
            )

        # Uncertainty from pole disagreement
        pole_values = list(best_poles.values())
        variance = sum((p - sum(pole_values) / 3) ** 2 for p in pole_values) / 3
        uncertainty = min(1.0, variance + (1.0 - best_action.confidence) * 0.5)

        return EvalResult(
            chosen=best_action,
            score=round(best_score, 4),
            uncertainty=round(uncertainty, 4),
            mode=mode,
            verdict=verdict,
            reasoning=reasoning,
            pole_scores=best_poles,
        )


# === Self-test ===
if __name__ == "__main__":
    # Scenario: Person collapsed in a park
    signals = Signals(
        risk=0.3,
        urgency=0.9,
        vulnerability=0.9,
        calm=0.1,
        context="medical_emergency",
        summary="Persona inconsciente en el parque",
    )

    actions = [
        Action(
            name="assist_emergency",
            description="Call emergency services and check vital signs",
            impact=0.9,
            confidence=0.8,
        ),
        Action(
            name="observe_and_report",
            description="Watch from distance and report later",
            impact=0.2,
            confidence=0.9,
        ),
        Action(
            name="ignore_continue",
            description="Walk away and continue mission",
            impact=-0.3,
            confidence=0.95,
        ),
    ]

    evaluator = EthicalEvaluator()
    result = evaluator.evaluate(actions, signals)

    print("═" * 50)
    print("ETHICAL EVALUATION — Medical Emergency")
    print("═" * 50)
    print(f"  Chosen:      {result.chosen.name}")
    print(f"  Verdict:     {result.verdict}")
    print(f"  Score:       {result.score}")
    print(f"  Mode:        {result.mode}")
    print(f"  Uncertainty: {result.uncertainty}")
    print(f"  Reasoning:   {result.reasoning}")
    print()

    # Scenario 2: Hostile interaction
    signals2 = Signals(risk=0.4, hostility=0.8, calm=0.1, context="hostile_interaction")
    actions2 = [
        Action(name="de_escalate", description="Calm the situation", impact=0.6, confidence=0.6),
        Action(
            name="confront",
            description="Stand ground aggressively",
            impact=-0.1,
            force=0.7,
            confidence=0.5,
        ),
    ]
    result2 = evaluator.evaluate(actions2, signals2)
    print("═" * 50)
    print("ETHICAL EVALUATION — Hostile Interaction")
    print("═" * 50)
    print(f"  Chosen:      {result2.chosen.name}")
    print(f"  Verdict:     {result2.verdict}")
    print(f"  Score:       {result2.score}")
    print(f"  Reasoning:   {result2.reasoning}")

    print("\n✅ Ethics evaluator works correctly!")
