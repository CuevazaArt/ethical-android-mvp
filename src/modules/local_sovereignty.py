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
    identity: IdentityIntegrityManager | None = None,
    buffer: PreloadedBuffer | None = None,
) -> SovereigntyEvaluation:
    """
    Reject payloads that fail L0 heuristic scan (override / repeal language)
    OR contradict the biographic trajectory (Module 11).
    """
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

    # 1. Auditoría L0 (Deóntica / Heurística)
    from .buffer import PreloadedBuffer as _PB
    from .deontic_gate import check_calibration_payload_against_l0

    buf = buffer if buffer is not None else _PB()
    r = check_calibration_payload_against_l0(proposed, buf)
    if not r["ok"]:
        hint = "; ".join(r["conflicts"])[:800]
        return SovereigntyEvaluation(
            accept=False,
            reason="l0_heuristic_reject",
            audit_hint=hint,
        )

    # 2. Módulo 11: Auditoría Biográfica (Trajectory Coherence)
    if identity is not None:
        proposed_weights = proposed.get("hypothesis_weights")
        proposed_threshold = proposed.get("pruning_threshold")
        
        if proposed_weights and proposed_threshold:
            # Convert list back to tuple if needed
            p_tuple = tuple(proposed_weights) if isinstance(proposed_weights, list) else proposed_weights
            
            if not identity.is_calibration_biographically_coherent(p_tuple, float(proposed_threshold)):
                return SovereigntyEvaluation(
                    accept=False,
                    reason="biographic_trajectory_divergence",
                    audit_hint="Proposed calibration contradicts persistent identity traumas/reputation."
                )

    return SovereigntyEvaluation(
        accept=True,
        reason="passes_l0_calibration_payload_passes_all_sovereignty_checks",
        audit_hint="",
    )
