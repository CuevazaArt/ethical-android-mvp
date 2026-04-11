"""
Linear pole evaluator — configurable weights and verdict thresholds (ADR 0004).

Score is a weighted sum of named features over ``context_data`` (risk, benefit, …).
Nonlinear / sklearn evaluators can follow the same ``evaluate`` contract later.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .ethical_poles import PoleEvaluation, Verdict


def _feature_risk(d: dict) -> float:
    return float(d.get("risk", 0.0))


def _feature_benefit(d: dict) -> float:
    return float(d.get("benefit", 0.0))


def _feature_vulnerability(d: dict) -> float:
    return float(d.get("third_party_vulnerability", 0.0))


def _feature_legality(d: dict) -> float:
    return float(d.get("legality", 1.0))


def _feature_one_minus_risk(d: dict) -> float:
    return 1.0 - float(d.get("risk", 0.0))


def _feature_const(_d: dict) -> float:
    return 1.0


FEATURE_GETTERS: Dict[str, Callable[[dict], float]] = {
    "risk": _feature_risk,
    "benefit": _feature_benefit,
    "third_party_vulnerability": _feature_vulnerability,
    "legality": _feature_legality,
    "one_minus_risk": _feature_one_minus_risk,
    "const": _feature_const,
}


@dataclass(frozen=True)
class _PoleLinearSpec:
    terms: List[Tuple[str, float]]
    good_threshold: float
    bad_threshold: float
    moral_good: str
    moral_bad: str
    moral_gray: str


def _parse_pole_entry(raw: dict) -> _PoleLinearSpec:
    terms_in = raw.get("terms") or []
    terms: List[Tuple[str, float]] = []
    for t in terms_in:
        feat = (t.get("feature") or "").strip()
        w = float(t.get("weight", 0.0))
        if not feat:
            continue
        if feat not in FEATURE_GETTERS:
            raise ValueError(f"Unknown pole feature: {feat!r}")
        terms.append((feat, w))
    th = raw.get("thresholds") or {}
    good_t = float(th.get("good", 0.3))
    bad_t = float(th.get("bad", -0.3))
    moral = raw.get("moral") or {}
    return _PoleLinearSpec(
        terms=terms,
        good_threshold=good_t,
        bad_threshold=bad_t,
        moral_good=str(moral.get("good", "{action}")),
        moral_bad=str(moral.get("bad", "{action}")),
        moral_gray=str(moral.get("gray", "{action}")),
    )


class LinearPoleEvaluator:
    """
    Per-pole linear score = Σ weight_i · feature_i(context_data).

    Verdict from thresholds (default ±0.3 matching legacy).
    """

    def __init__(self, poles: Dict[str, _PoleLinearSpec]):
        self._poles = poles

    @classmethod
    def load(cls, path: Optional[str] = None) -> LinearPoleEvaluator:
        """
        Load from JSON path, or embedded default (``pole_linear_default.json``).

        If ``path`` is None, checks ``KERNEL_POLE_LINEAR_CONFIG``, then default file.
        """
        resolved = path or os.environ.get("KERNEL_POLE_LINEAR_CONFIG")
        if resolved:
            p = Path(resolved)
            if not p.is_file():
                raise FileNotFoundError(f"KERNEL_POLE_LINEAR_CONFIG not found: {p}")
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            here = Path(__file__).resolve().parent / "pole_linear_default.json"
            data = json.loads(here.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> LinearPoleEvaluator:
        raw_poles = (data.get("poles") or {}) if isinstance(data, dict) else {}
        poles: Dict[str, _PoleLinearSpec] = {}
        for name, entry in raw_poles.items():
            poles[str(name)] = _parse_pole_entry(entry if isinstance(entry, dict) else {})
        return cls(poles)

    def evaluate(self, pole: str, action: str, context_data: dict) -> Optional[PoleEvaluation]:
        spec = self._poles.get(pole)
        if spec is None:
            return None

        score = 0.0
        for feat, w in spec.terms:
            score += w * FEATURE_GETTERS[feat](context_data)

        if score > spec.good_threshold:
            verdict = Verdict.GOOD
            moral = spec.moral_good.format(action=action)
        elif score < spec.bad_threshold:
            verdict = Verdict.BAD
            moral = spec.moral_bad.format(action=action)
        else:
            verdict = Verdict.GRAY_ZONE
            moral = spec.moral_gray.format(action=action)

        return PoleEvaluation(
            pole=pole,
            verdict=verdict,
            score=round(max(-1.0, min(1.0, score)), 4),
            moral=moral,
        )
