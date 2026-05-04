# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Maturity Stage Envelope (V2.151)

Tracks the kernel's developmental stage and enforces a confidence ceiling
so that displayed certainty is bounded by the stage's earned epistemic range.

Rules:
- Stages: infant → child → adolescent → young_adult
- Each stage defines a ``confidence_ceiling``: the maximum value the kernel
  may display as its certainty, regardless of internal computed confidence.
- ``requires_external_promotion = True`` always: the kernel NEVER promotes
  itself.  Promotions are operator-signed entries in
  ``docs/governance/MATURITY_PROMOTIONS.jsonl``.

The active stage is resolved at import time from the governance ledger so that
every chat turn carries the correct envelope without repeated I/O.

Usage::

    from src.core.maturity import current_stage, apply_confidence_ceiling

    stage = current_stage()
    displayed = apply_confidence_ceiling(internal_confidence=0.95)
    # → 0.55 if stage is infant
"""

from __future__ import annotations

import json
import logging
import os
from enum import Enum
from pathlib import Path

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stage definition
# ---------------------------------------------------------------------------

_GOVERNANCE_LEDGER = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "governance"
    / "MATURITY_PROMOTIONS.jsonl"
)


class MaturityStage(str, Enum):
    """Ordered developmental stages of the ethical kernel.

    Each stage name is also its string representation so that JSON
    serialisation works without extra converters.
    """

    infant = "infant"
    child = "child"
    adolescent = "adolescent"
    young_adult = "young_adult"

    # Intrinsic ordering — lower ordinal = earlier stage
    @property
    def ordinal(self) -> int:
        return list(MaturityStage).index(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, MaturityStage):
            return NotImplemented  # type: ignore[return-value]
        return self.ordinal < other.ordinal

    def __le__(self, other: object) -> bool:
        if not isinstance(other, MaturityStage):
            return NotImplemented  # type: ignore[return-value]
        return self.ordinal <= other.ordinal


# ---------------------------------------------------------------------------
# Per-stage parameters
# ---------------------------------------------------------------------------

#: Maximum confidence value the kernel may *display* at each stage.
#: Internal computed confidence is preserved but capped before exposure.
CONFIDENCE_CEILING: dict[MaturityStage, float] = {
    MaturityStage.infant: 0.55,
    MaturityStage.child: 0.70,
    MaturityStage.adolescent: 0.82,
    MaturityStage.young_adult: 0.95,
}

#: A kernel at any stage always requires an external human promotion.
REQUIRES_EXTERNAL_PROMOTION: bool = True

# ---------------------------------------------------------------------------
# Governance ledger reader
# ---------------------------------------------------------------------------


def _load_promotions() -> list[dict]:
    """Read all valid promotion entries from the governance ledger.

    Returns an empty list if the file does not exist or is malformed.
    Individual lines that fail to parse are skipped with a warning.
    """
    if not _GOVERNANCE_LEDGER.exists():
        return []
    entries: list[dict] = []
    try:
        with _GOVERNANCE_LEDGER.open(encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                    entries.append(obj)
                except json.JSONDecodeError as exc:
                    _log.warning(
                        "MATURITY_PROMOTIONS.jsonl line %d skipped: %s", lineno, exc
                    )
    except OSError as exc:
        _log.warning("Cannot read maturity promotions ledger: %s", exc)
    return entries


def _resolve_stage_from_ledger() -> MaturityStage:
    """Determine the active stage from the governance ledger.

    Only entries with ``"type": "promotion"`` and a valid ``"to_stage"``
    field count.  The highest-ordinal valid stage wins.
    Defaults to ``MaturityStage.infant`` if no valid promotions exist.
    """
    entries = _load_promotions()
    active = MaturityStage.infant
    for entry in entries:
        if entry.get("type") != "promotion":
            continue
        raw_stage = entry.get("to_stage", "")
        try:
            candidate = MaturityStage(raw_stage)
        except ValueError:
            _log.warning("Unknown to_stage %r in promotion entry; ignored.", raw_stage)
            continue
        if candidate > active:
            active = candidate
    return active


# ---------------------------------------------------------------------------
# Module-level cached stage (resolved once at import)
# ---------------------------------------------------------------------------

_CACHED_STAGE: MaturityStage | None = None


def current_stage(*, force_reload: bool = False) -> MaturityStage:
    """Return the currently active MaturityStage.

    The result is cached at module level to avoid repeated disk I/O.
    Pass ``force_reload=True`` in tests or after a manual ledger write.

    The environment variable ``KERNEL_MATURITY_STAGE_OVERRIDE`` can set a
    stage directly (useful in CI without a governance ledger).
    """
    global _CACHED_STAGE

    # Env override (CI / test convenience only)
    env_override = os.environ.get("KERNEL_MATURITY_STAGE_OVERRIDE", "").strip().lower()
    if env_override:
        try:
            return MaturityStage(env_override)
        except ValueError:
            _log.warning(
                "Invalid KERNEL_MATURITY_STAGE_OVERRIDE=%r; ignored.", env_override
            )

    if _CACHED_STAGE is None or force_reload:
        _CACHED_STAGE = _resolve_stage_from_ledger()
    return _CACHED_STAGE


def apply_confidence_ceiling(internal_confidence: float) -> float:
    """Cap ``internal_confidence`` to the current stage's ceiling.

    - Non-finite inputs are replaced with 0.0.
    - The result is always in [0.0, ceiling].

    Args:
        internal_confidence: The raw computed confidence (e.g. from
            ``EvalResult.evaluation.chosen.confidence``).

    Returns:
        A float in [0.0, ``CONFIDENCE_CEILING[current_stage()]``].
    """
    import math

    if not math.isfinite(internal_confidence):
        internal_confidence = 0.0
    internal_confidence = max(0.0, min(1.0, internal_confidence))
    ceiling = CONFIDENCE_CEILING[current_stage()]
    return min(internal_confidence, ceiling)
