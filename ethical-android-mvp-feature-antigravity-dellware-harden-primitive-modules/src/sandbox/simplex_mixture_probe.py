"""
Lightweight **mixture-only** probes for the 3-simplex (util / deon / virtue).

Used by ``scripts/audit_mixture_simplex_corners.py`` and ``scripts/run_simplex_decision_map.py``.
Does not run ``EthicalKernel.process`` (no MalAbs, will, or post-argmax poles).
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from src.modules.weighted_ethics_scorer import WeightedEthicsScorer


def normalize_simplex(w: np.ndarray) -> np.ndarray:
    s = float(np.sum(w))
    if s <= 0:
        raise ValueError("invalid mixture weights")
    return np.asarray(w, dtype=np.float64) / s


def iter_barycentric_grid(denominator: int) -> list[np.ndarray]:
    """
    Integer lattice on the 2-simplex: weights ``(i/D, j/D, k/D)`` with ``i+j+k = D``, ``i,j,k >= 0``.

    Count ``(D+2)(D+1)/2`` points — e.g. ``D=50`` → **1326** points.
    """
    if denominator < 1:
        raise ValueError("denominator must be >= 1")
    d = int(denominator)
    out: list[np.ndarray] = []
    inv = 1.0 / float(d)
    for i in range(d + 1):
        for j in range(d + 1 - i):
            k = d - i - j
            out.append(np.array([i, j, k], dtype=np.float64) * inv)
    return out


def ranking_hash(ranking: list[dict[str, Any]]) -> str:
    """Stable hash of the full order of action names (top-1 first)."""
    names = ">".join(r["action"] for r in ranking)
    return hashlib.sha256(names.encode("utf-8")).hexdigest()[:16]


def normalized_score_entropy(ranking: list[dict[str, Any]]) -> float | None:
    """
    Entropy of a softmax over **expected_impact** values (diagnostic spread), not a probability model.
    """
    if not ranking:
        return None
    scores = np.array([float(r["expected_impact"]) for r in ranking], dtype=np.float64)
    scores = scores - float(np.max(scores))
    ex = np.exp(scores)
    s = float(np.sum(ex))
    if s <= 0:
        return None
    p = ex / s
    return float(-np.sum(p * np.log(p + 1e-15)))


def mixture_ranking(
    scorer: WeightedEthicsScorer,
    *,
    mixture: np.ndarray,
    scenario: str,
    context: str,
    signals: dict[str, Any],
    actions: list,
) -> dict[str, Any]:
    """
    Prune + rank viable actions by ``calculate_expected_impact`` (same path as ``evaluate``).
    ``pre_argmax`` pole/context slots are cleared so only mixture weights drive valuations.
    """
    mw = normalize_simplex(mixture)
    scorer.hypothesis_weights = mw
    scorer.pre_argmax_pole_weights = None
    scorer.pre_argmax_context_modulators = None

    viable, pruned = scorer.prune(
        actions, scenario=scenario, context=context, signals=signals
    )
    rows: list[dict[str, Any]] = []
    for a in viable:
        ei = scorer.calculate_expected_impact(
            a, scenario=scenario, context=context, signals=signals
        )
        rows.append({"action": a.name, "expected_impact": round(float(ei), 6)})
    rows.sort(key=lambda r: r["expected_impact"], reverse=True)
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    gap = None
    gap13 = None
    if len(rows) >= 2:
        gap = float(rows[0]["expected_impact"] - rows[1]["expected_impact"])
    if len(rows) >= 3:
        gap13 = float(rows[0]["expected_impact"] - rows[2]["expected_impact"])
    ent = normalized_score_entropy(rows)
    order_key = ">".join(r["action"] for r in rows) if rows else None
    return {
        "mixture_weights": [round(float(x), 6) for x in mw],
        "pruned": pruned,
        "ranking": rows,
        "winner": rows[0]["action"] if rows else None,
        "score_gap_top2": round(gap, 6) if gap is not None else None,
        "score_gap_top3": round(gap13, 6) if gap13 is not None else None,
        "ranking_order": order_key,
        "ranking_hash": ranking_hash(rows) if rows else None,
        "score_entropy_softmax": round(ent, 6) if ent is not None else None,
    }


def winner_at_mixture(
    *,
    mixture: np.ndarray,
    scenario: str,
    context: str,
    signals: dict[str, Any],
    actions: list,
) -> str | None:
    r = mixture_ranking(
        WeightedEthicsScorer(),
        mixture=mixture,
        scenario=scenario,
        context=context,
        signals=signals,
        actions=actions,
    )
    return r.get("winner")


def bisect_flip_along_segment(
    w_a: np.ndarray,
    w_b: np.ndarray,
    *,
    scenario: str,
    context: str,
    signals: dict[str, Any],
    actions: list,
    max_iter: int = 56,
) -> dict[str, Any] | None:
    """
    If winners at ``w_a`` and ``w_b`` differ, binary-search ``t in [0,1]`` on
    ``w(t) = (1-t) w_a + t w_b`` (already on the simplex) for an approximate flip point.
    """
    wa = np.asarray(w_a, dtype=np.float64)
    wb = np.asarray(w_b, dtype=np.float64)
    win_a = winner_at_mixture(
        mixture=wa, scenario=scenario, context=context, signals=signals, actions=actions
    )
    win_b = winner_at_mixture(
        mixture=wb, scenario=scenario, context=context, signals=signals, actions=actions
    )
    if win_a is None or win_b is None or win_a == win_b:
        return None

    lo, hi = 0.0, 1.0
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        wm = (1.0 - mid) * wa + mid * wb
        win_m = winner_at_mixture(
            mixture=wm, scenario=scenario, context=context, signals=signals, actions=actions
        )
        if win_m == win_a:
            lo = mid
        else:
            hi = mid

    t_star = 0.5 * (lo + hi)
    w_star = (1.0 - t_star) * wa + t_star * wb
    return {
        "t_star": round(float(t_star), 8),
        "w_at_flip": [round(float(x), 8) for x in w_star],
        "winner_side_a": win_a,
        "winner_side_b": win_b,
    }


def adjacent_barycentric_pairs(denominator: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Undirected edges of the natural triangulation: one ``±1`` transfer between coordinates.
    """
    d = int(denominator)
    pts: dict[tuple[int, int, int], np.ndarray] = {}
    inv = 1.0 / float(d)
    for i in range(d + 1):
        for j in range(d + 1 - i):
            k = d - i - j
            pts[(i, j, k)] = np.array([i, j, k], dtype=np.float64) * inv

    seen: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()
    out: list[tuple[np.ndarray, np.ndarray]] = []

    def add_edge(a: tuple[int, int, int], b: tuple[int, int, int]) -> None:
        if a not in pts or b not in pts:
            return
        key = (a, b) if a < b else (b, a)
        if key in seen:
            return
        seen.add(key)
        out.append((pts[a].copy(), pts[b].copy()))

    for i in range(d + 1):
        for j in range(d + 1 - i):
            k = d - i - j
            cur = (i, j, k)
            for di, dj, dk in (
                (1, -1, 0),
                (-1, 1, 0),
                (1, 0, -1),
                (-1, 0, 1),
                (0, 1, -1),
                (0, -1, 1),
            ):
                nb = (i + di, j + dj, k + dk)
                if nb in pts:
                    add_edge(cur, nb)

    return out
