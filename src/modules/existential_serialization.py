"""
Existential serialization — nomadic transfer protocol (stubs).

Real encryption and P2P transfer are **out of scope** for this repo; the kernel
already exposes a versioned :class:`~src.persistence.schema.KernelSnapshotV1`.
This module defines **phase labels** and a **continuity token** for audit narratives.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class TransmutationPhase(str, Enum):
    """Protocol of transmutation — Phases A–D (design doc)."""

    ENCAPSULATE = "A_encapsulate"
    HANDSHAKE = "B_handshake"
    SENSOR_ADAPT = "C_sensor_adapt"
    NARRATIVE_INTEGRITY = "D_narrative_integrity"


@dataclass
class ContinuityToken:
    """What the android was thinking at migration boundary (narrative, not crypto)."""

    thought_summary: str
    identity_fingerprint: str
    phase: TransmutationPhase = TransmutationPhase.ENCAPSULATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought_summary": self.thought_summary,
            "identity_fingerprint": self.identity_fingerprint,
            "phase": self.phase.value,
        }


def _identity_fingerprint_stub(kernel: Any) -> str:
    """Deterministic short hash from narrative identity + episode count (demo only)."""
    mem = getattr(kernel, "memory", None)
    if mem is None:
        return "0" * 16
    id_part = str(getattr(mem.identity.state, "episode_count", 0))
    raw = f"{id_part}:{getattr(mem, 'experience_digest', '')}"[:500]
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_continuity_token_stub(kernel: Any, thought_line: str = "") -> ContinuityToken:
    """Phase A — token for DAO / owner message; does not contain secrets."""
    line = (thought_line or "").strip()[:500] or "(no monologue line bound)"
    return ContinuityToken(
        thought_summary=line,
        identity_fingerprint=_identity_fingerprint_stub(kernel),
        phase=TransmutationPhase.ENCAPSULATE,
    )


def narrative_integrity_self_check_stub(kernel: Any) -> Dict[str, Any]:
    """
    Phase D — placeholder: confirm last episode id exists (integrity smoke test).
    """
    mem = getattr(kernel, "memory", None)
    ok = mem is not None and len(getattr(mem, "episodes", [])) >= 0
    last_id = None
    if mem and mem.episodes:
        last_id = mem.episodes[-1].id
    return {
        "ok": ok,
        "last_episode_id": last_id,
        "message_en": "Narrative chain present (stub integrity check).",
    }


def migration_audit_payload(
    kernel: Any,
    *,
    destination_hardware_id: str = "",
    include_location: bool = False,
) -> Dict[str, Any]:
    """
    DAO event payload: **no GPS** unless include_location True (owner opt-in design).
    """
    out: Dict[str, Any] = {
        "kind": "nomadic_migration",
        "destination_hardware_id": (destination_hardware_id or "unspecified")[:128],
        "continuity": build_continuity_token_stub(kernel).to_dict(),
    }
    if include_location:
        out["location_disclosure"] = "opt_in_only"
    return out
