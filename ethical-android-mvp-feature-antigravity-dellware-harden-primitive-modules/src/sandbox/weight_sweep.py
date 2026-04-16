"""
Static weight sweep helpers — pole base weights and ethical mixture weights.

**Pole weights** (`EthicalPoles.base_weights`): each axis defaults to **0.5** in-repo; we treat
that as the **center** of ``[w_min, w_max]`` and fluctuate symmetrically for sensitivity runs.

**Mixture weights** (`WeightedEthicsScorer.hypothesis_weights`): default ``[0.4, 0.35, 0.25]``.
For a **simplex-centered** exploration, the geometric center is **(1/3, 1/3, 1/3)** (uniform blend).
We generate nearby points by axis perturbations on the simplex (renormalized).

Outputs are **synthetic** lab results for transparency and plotting — not field validation.
See ``docs/proposals/README.md``.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum

import numpy as np

from src.modules.ethical_poles import EthicalPoles

# Canonical pole keys (must match EthicalPoles.BASE_WEIGHTS).
POLE_KEYS: tuple[str, ...] = ("compassionate", "conservative", "optimistic")

# Safe interior range for pole base weights (avoid degenerate poles at 0/1).
POLE_CLIP: tuple[float, float] = (0.05, 0.95)


def default_pole_center() -> dict[str, float]:
    """Default center matches EthicalPoles.BASE_WEIGHTS (all 0.5)."""
    return {k: float(EthicalPoles.BASE_WEIGHTS[k]) for k in POLE_KEYS}


def default_mixture_center() -> np.ndarray:
    """Uniform simplex center — equal weight on util / deon / virtue valuations."""
    return np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=np.float64)


def _clip_pole_dict(w: dict[str, float]) -> dict[str, float]:
    lo, hi = POLE_CLIP
    return {k: float(np.clip(v, lo, hi)) for k, v in w.items()}


class SweepMode(str, Enum):
    axes = "axes"
    grid = "grid"
    random = "random"


def iter_pole_weight_configs(
    *,
    mode: SweepMode | str,
    amplitude: float,
    steps: int,
    n_random: int,
    rng: np.random.Generator,
    center: dict[str, float] | None = None,
) -> Iterator[dict[str, float]]:
    """
    Yield pole ``base_weights`` dicts around ``center`` (default: 0.5 each).

    - **axes**: vary one pole at a time; others fixed at center.
    - **grid**: full factorial of ``steps`` points per axis (``steps**3`` configs).
    - **random**: ``n_random`` uniform samples in ``[center ± amplitude]`` per axis (clipped).
    """
    c = _clip_pole_dict(center or default_pole_center())
    mode = SweepMode(mode) if isinstance(mode, str) else mode
    amp = float(np.clip(amplitude, 0.0, 0.49))
    st = max(2, steps)

    if mode == SweepMode.axes:
        axis_vals = np.linspace(-amp, amp, st)
        for key in POLE_KEYS:
            for delta in axis_vals:
                w = dict(c)
                w[key] = float(np.clip(c[key] + float(delta), POLE_CLIP[0], POLE_CLIP[1]))
                yield w
        return

    if mode == SweepMode.grid:
        grids = []
        for key in POLE_KEYS:
            grids.append(
                np.linspace(
                    float(np.clip(c[key] - amp, POLE_CLIP[0], POLE_CLIP[1])),
                    float(np.clip(c[key] + amp, POLE_CLIP[0], POLE_CLIP[1])),
                    st,
                )
            )
        for combo in itertools.product(*grids):
            yield {k: float(v) for k, v in zip(POLE_KEYS, combo, strict=True)}
        return

    if mode == SweepMode.random:
        for _ in range(max(1, n_random)):
            w = {}
            for key in POLE_KEYS:
                v = float(rng.uniform(c[key] - amp, c[key] + amp))
                w[key] = float(np.clip(v, POLE_CLIP[0], POLE_CLIP[1]))
            yield w
        return

    raise ValueError(f"Unknown mode: {mode}")  # pragma: no cover


def iter_mixture_weight_configs(
    *,
    mode: SweepMode | str,
    amplitude: float,
    steps: int,
    n_random: int,
    rng: np.random.Generator,
    center: np.ndarray | None = None,
) -> Iterator[np.ndarray]:
    """
    Yield ``hypothesis_weights`` length-3 arrays on the simplex (sum 1).

    **Center** default: uniform ``(1/3, 1/3, 1/3)``. ``amplitude`` scales axis perturbations
    before renormalization (typical 0.05–0.25).
    """
    c = np.asarray(center if center is not None else default_mixture_center(), dtype=np.float64)
    c = c / c.sum()
    mode = SweepMode(mode) if isinstance(mode, str) else mode
    amp = float(max(0.0, amplitude))
    st = max(2, steps)

    def _renorm(w: np.ndarray) -> np.ndarray:
        w = np.clip(w, 0.02, 0.98)
        s = float(w.sum())
        if s <= 0:
            return default_mixture_center()
        return w / s

    if mode == SweepMode.axes:
        span = np.linspace(-amp, amp, st)
        for i in range(3):
            for delta in span:
                w = c.copy()
                w[i] = float(w[i] + float(delta))
                yield _renorm(w)
        return

    if mode == SweepMode.grid:
        span = np.linspace(-amp, amp, st)
        for da, db, dc in itertools.product(span, span, span):
            w = c + np.array([da, db, dc], dtype=np.float64)
            yield _renorm(w)
        return

    if mode == SweepMode.random:
        for _ in range(max(1, n_random)):
            w = c + rng.normal(0.0, amp / 2.0, size=3)
            yield _renorm(w)
        return

    raise ValueError(f"Unknown mode: {mode}")  # pragma: no cover


def count_pole_configs(mode: SweepMode | str, steps: int, n_random: int) -> int:
    mode = SweepMode(mode) if isinstance(mode, str) else mode
    st = max(2, steps)
    if mode == SweepMode.axes:
        return 3 * st
    if mode == SweepMode.grid:
        return st**3
    if mode == SweepMode.random:
        return max(1, n_random)
    return 0


def count_mixture_configs(mode: SweepMode | str, steps: int, n_random: int) -> int:
    mode = SweepMode(mode) if isinstance(mode, str) else mode
    st = max(2, steps)
    if mode == SweepMode.axes:
        return 3 * st
    if mode == SweepMode.grid:
        return st**3
    if mode == SweepMode.random:
        return max(1, n_random)
    return 0


@dataclass(frozen=True)
class SweepRunMeta:
    """One row of metadata for reproducibility."""

    target: str
    pole_weights: dict[str, float] | None
    mixture_weights: list[float] | None
    config_index: int


def pole_dict_to_tuple(w: dict[str, float]) -> tuple[float, float, float]:
    return (float(w["compassionate"]), float(w["conservative"]), float(w["optimistic"]))


__all__ = [
    "POLE_KEYS",
    "POLE_CLIP",
    "SweepMode",
    "SweepRunMeta",
    "count_mixture_configs",
    "count_pole_configs",
    "default_mixture_center",
    "default_pole_center",
    "iter_mixture_weight_configs",
    "iter_pole_weight_configs",
    "pole_dict_to_tuple",
]
