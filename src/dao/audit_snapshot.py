"""
E2 — Audit snapshot API (ADR 0016 Axis E2).

Provides a structured, serialisable view of the current kernel decision
state for DAO audit and governance review. Consumed by MockDAO.register_audit
and by kernel.export_audit_snapshot().

The snapshot is deliberately **read-only**: it describes what happened; it
does not feed back into the decision pipeline. This maintains the invariant
that DAO operations are advisory (WEAKNESSES §4).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.kernel import KernelDecision


@dataclass
class AuditSnapshot:
    """
    A point-in-time audit record of a kernel decision.

    All fields are JSON-serialisable primitives (no numpy types, no
    complex objects). ``to_dict()`` / ``to_json()`` produce the canonical
    wire format for the MockDAO sidecar.
    """

    # Identity
    snapshot_schema: str = "audit_snapshot_v1"
    snapshot_id: str = ""  # SHA-256 of canonical content (set by build_audit_snapshot)
    captured_at: str = ""  # ISO-8601 UTC

    # Kernel identity
    agent_id: str = "unknown"
    session_turn: int = 0

    # Decision provenance
    scenario: str = ""
    place: str = ""
    context_key: str = ""  # mixture_context_key / hierarchical_context_key
    final_action: str = ""
    decision_mode: str = ""
    blocked: bool = False
    block_reason: str = ""

    # Scoring transparency (ADR 0012)
    applied_mixture_weights: list[float] = field(default_factory=list)
    bma_win_probabilities: dict[str, float] = field(default_factory=dict)
    mixture_posterior_alpha: list[float] = field(default_factory=list)
    feedback_consistency: str = ""

    # Moral verdict
    moral_score: float | None = None
    moral_verdict: str = ""

    # Safety signals
    absolute_evil_blocked: bool = False
    perception_coercion_uncertainty: float | None = None

    # Sensor state at decision time
    battery_fraction: float | None = None
    accelerometer_jerk: float | None = None
    ambient_noise: float | None = None

    # Governable parameters in effect at snapshot time
    active_governable_values: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, indent=indent)

    @property
    def is_safe(self) -> bool:
        """Quick predicate: decision was not blocked and not absolute-evil."""
        return not self.blocked and not self.absolute_evil_blocked


def _sha256_of_dict(d: dict[str, Any]) -> str:
    canonical = json.dumps(d, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _current_governable_values() -> dict[str, Any]:
    """
    Read the current effective values of all governable env-var parameters.
    Only reads; never writes.
    """
    import os

    from src.dao.governable_parameters import GOVERNABLE_PARAMETERS

    result: dict[str, Any] = {}
    for name, spec in GOVERNABLE_PARAMETERS.items():
        if spec.env_var:
            raw = os.environ.get(spec.env_var, "").strip()
            if raw:
                result[name] = raw
            else:
                result[name] = spec.default_value
    return result


def build_audit_snapshot(
    decision: KernelDecision,
    *,
    agent_id: str = "unknown",
    session_turn: int = 0,
    sensor_snapshot: Any = None,
) -> AuditSnapshot:
    """
    Build an :class:`AuditSnapshot` from a completed :class:`KernelDecision`.

    Parameters
    ----------
    decision:
        The kernel decision to snapshot.
    agent_id:
        The agent / session identifier.
    session_turn:
        Turn counter within the session.
    sensor_snapshot:
        Optional ``SensorSnapshot`` instance; used to populate battery /
        accelerometer / noise fields if present.
    """
    captured_at = datetime.now(UTC).isoformat()

    # Moral verdict
    moral_score: float | None = None
    moral_verdict: str = ""
    if decision.moral is not None:
        moral_score = float(decision.moral.total_score)
        moral_verdict = getattr(
            decision.moral.global_verdict, "value", str(decision.moral.global_verdict)
        )

    # Mixture weights
    amw: list[float] = []
    if decision.applied_mixture_weights:
        amw = [float(w) for w in decision.applied_mixture_weights]

    bma_win: dict[str, float] = {}
    if decision.bma_win_probabilities:
        bma_win = {k: float(v) for k, v in decision.bma_win_probabilities.items()}

    mpa: list[float] = []
    if decision.mixture_posterior_alpha:
        mpa = [float(a) for a in decision.mixture_posterior_alpha]

    # Sensor
    batt = jerk = noise = None
    if sensor_snapshot is not None:
        batt = getattr(sensor_snapshot, "battery_level", None)
        jerk = getattr(sensor_snapshot, "accelerometer_jerk", None)
        noise = getattr(sensor_snapshot, "ambient_noise", None)

    # Absolute evil
    abs_evil_blocked = bool(
        decision.absolute_evil and getattr(decision.absolute_evil, "blocked", False)
    )

    snap = AuditSnapshot(
        captured_at=captured_at,
        agent_id=agent_id,
        session_turn=session_turn,
        scenario=decision.scenario,
        place=decision.place,
        context_key=decision.mixture_context_key or decision.hierarchical_context_key or "",
        final_action=decision.final_action,
        decision_mode=decision.decision_mode,
        blocked=decision.blocked,
        block_reason=decision.block_reason,
        applied_mixture_weights=amw,
        bma_win_probabilities=bma_win,
        mixture_posterior_alpha=mpa,
        feedback_consistency=decision.feedback_consistency or "",
        moral_score=moral_score,
        moral_verdict=moral_verdict,
        absolute_evil_blocked=abs_evil_blocked,
        battery_fraction=batt,
        accelerometer_jerk=jerk,
        ambient_noise=noise,
        active_governable_values=_current_governable_values(),
    )
    snap.snapshot_id = _sha256_of_dict(
        {
            "final_action": snap.final_action,
            "captured_at": snap.captured_at,
            "agent_id": snap.agent_id,
            "session_turn": snap.session_turn,
        }
    )
    return snap
