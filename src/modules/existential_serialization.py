"""
Existential serialization — nomadic transfer protocol (stubs).

Real encryption and P2P transfer are **out of scope** for this repo; the kernel
already exposes a versioned :class:`~src.persistence.schema.KernelSnapshotV1`.
This module defines **phase labels** and a **continuity token** for audit narratives.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .hub_audit import register_hub_calibration


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


def nomad_migration_audit_enabled() -> bool:
    """Append DAO audit line when simulating / completing a nomadic handoff."""
    v = os.environ.get("KERNEL_NOMAD_MIGRATION_AUDIT", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def nomad_simulation_ws_enabled() -> bool:
    """WebSocket JSON ``nomad_simulate_migration`` (demo / lab)."""
    v = os.environ.get("KERNEL_NOMAD_SIMULATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def migration_audit_payload(
    kernel: Any,
    *,
    destination_hardware_id: str = "",
    include_location: bool = False,
    thought_line: str = "",
) -> Dict[str, Any]:
    """
    DAO event payload: **no GPS** unless include_location True (owner opt-in design).
    """
    out: Dict[str, Any] = {
        "kind": "nomadic_migration",
        "destination_hardware_id": (destination_hardware_id or "unspecified")[:128],
        "continuity": build_continuity_token_stub(kernel, thought_line).to_dict(),
    }
    if include_location:
        out["location_disclosure"] = "opt_in_only"
    return out


def record_nomadic_migration_audit(
    dao: Any,
    kernel: Any,
    *,
    destination_hardware_id: str = "",
    include_location: bool = False,
    thought_line: str = "",
) -> bool:
    """Register a :class:`~src.modules.mock_dao.MockDAO` audit record when env allows."""
    if not nomad_migration_audit_enabled():
        return False
    payload = migration_audit_payload(
        kernel,
        destination_hardware_id=destination_hardware_id,
        include_location=include_location,
        thought_line=thought_line,
    )
    register_hub_calibration(dao, "nomadic_migration", payload)
    return True


def simulate_nomadic_migration(
    kernel: Any,
    dao: Any,
    *,
    profile: str = "mobile",
    destination_hardware_id: str = "",
    thought_line: str = "",
    include_location: bool = False,
) -> Dict[str, Any]:
    """
    Demo **Phase C**: apply HAL profile, optional DAO audit, narrative delta + integrity stub.

    ``profile``: ``\"mobile\"`` | ``\"server\"`` (default mobile = edge tier + phone sensors).
    """
    from .hardware_abstraction import (
        apply_hardware_context,
        default_mobile_context,
        default_server_context,
        sensor_delta_narrative,
    )

    before = getattr(kernel, "_hal_context", None)
    before_ctx = before if before is not None else default_server_context()
    after = default_mobile_context() if profile.strip().lower() == "mobile" else default_server_context()
    apply_hardware_context(kernel, after)
    narrative_en = sensor_delta_narrative(before_ctx, after)
    audit_recorded = record_nomadic_migration_audit(
        dao,
        kernel,
        destination_hardware_id=destination_hardware_id,
        include_location=include_location,
        thought_line=thought_line,
    )
    return {
        "profile": profile,
        "sensor_delta_narrative_en": narrative_en,
        "hardware_context": after.to_public_dict(),
        "integrity": narrative_integrity_self_check_stub(kernel),
        "dao_audit_recorded": audit_recorded,
    }
