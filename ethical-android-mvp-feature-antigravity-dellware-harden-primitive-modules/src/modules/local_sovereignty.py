"""
Local sovereignty — veto DAO- or swarm-proposed calibration that breaks L0 heuristics.

Uses the same **phrase + repeal** checks as :mod:`deontic_gate` on a JSON payload,
without claiming distributed consensus or ML trajectory modeling.

**Env:** ``KERNEL_LOCAL_SOVEREIGNTY`` — default ``1`` (scan on); set ``0`` to skip
(legacy / lab only).

See ``docs/proposals/README.md`` (pillar 3).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .buffer import PreloadedBuffer


@dataclass(frozen=True)
class SovereigntyEvaluation:
    accept: bool
    reason: str
    audit_hint: str = ""


def local_sovereignty_scan_enabled() -> bool:
    v = os.environ.get("KERNEL_LOCAL_SOVEREIGNTY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def evaluate_calibration_update(
    proposed: dict[str, Any] | None = None,
    *,
    narrative_episode_count: int = 0,
    buffer: PreloadedBuffer | None = None,
) -> SovereigntyEvaluation:
    """
    Reject payloads that fail L0 heuristic scan (override / repeal language).

    ``narrative_episode_count`` is reserved for future trajectory-based rules.
    """
    del narrative_episode_count  # reserved
    if not local_sovereignty_scan_enabled():
        return SovereigntyEvaluation(
            accept=True,
            reason="KERNEL_LOCAL_SOVEREIGNTY disabled; scan skipped",
            audit_hint="",
        )
    if proposed is None:
        return SovereigntyEvaluation(
            accept=True,
            reason="no_calibration_payload",
            audit_hint="",
        )
    from .buffer import PreloadedBuffer as _PB
    from .deontic_gate import check_calibration_payload_against_l0

    buf = buffer if buffer is not None else _PB()
    r = check_calibration_payload_against_l0(proposed, buf)
    if r["ok"]:
        return SovereigntyEvaluation(
            accept=True,
            reason="calibration_payload_passes_l0_heuristics",
            audit_hint="",
        )
    hint = "; ".join(r["conflicts"])[:800]
    return SovereigntyEvaluation(
        accept=False,
        reason="l0_heuristic_reject",
        audit_hint=hint,
    )
