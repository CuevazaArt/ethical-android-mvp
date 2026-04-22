"""
Nomad WebSocket session bootstrap (Bloque 22.2).

Builds a JSON-serializable ``[SYNC_IDENTITY]`` envelope so the PWA can align
PAD / glow with persisted narrative state after flaky mobile reconnects.
"""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from src.kernel_lobes.models import GestaltSnapshot

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def _finite_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _episode_stub(ep: Any) -> dict[str, Any]:
    pad = getattr(ep, "affect_pad", None)
    pad_list: list[float] | None = None
    if isinstance(pad, (list, tuple)) and len(pad) >= 3:
        pad_list = [
            _finite_float(pad[0], 0.0),
            _finite_float(pad[1], 0.0),
            _finite_float(pad[2], 0.0),
        ]
    return {
        "id": str(getattr(ep, "id", "")),
        "timestamp": str(getattr(ep, "timestamp", "")),
        "place": str(getattr(ep, "place", "")),
        "verdict": str(getattr(ep, "verdict", "")),
        "action_taken": str(getattr(ep, "action_taken", ""))[:240],
        "sigma": _finite_float(getattr(ep, "sigma", 0.5), 0.5),
        "context": str(getattr(ep, "context", "")),
        "affect_pad": pad_list,
    }


def build_sync_identity_payload(kernel: EthicalKernel) -> dict[str, Any]:
    """
    Snapshot + narrative base for the Nomad client (no WebSocket I/O here).
    """
    memory = kernel.memory
    episodes = getattr(memory, "episodes", []) or []
    tail = episodes[-12:] if episodes else []

    snap = GestaltSnapshot()
    if tail:
        last = tail[-1]
        snap.sigma = _finite_float(getattr(last, "sigma", snap.sigma), snap.sigma)
        pad = getattr(last, "affect_pad", None)
        if isinstance(pad, (list, tuple)) and len(pad) >= 3:
            snap.pad_state = (
                _finite_float(pad[0], 0.0),
                _finite_float(pad[1], 0.0),
                _finite_float(pad[2], 0.0),
            )
        arc_id = getattr(last, "arc_id", None)
        if arc_id:
            snap.active_arc_id = str(arc_id)

    identity = getattr(memory, "identity", None)
    reflection = ""
    narrative_identity: dict[str, Any] = {}
    if identity is not None:
        try:
            reflection = str(identity.ascription_line())
        except Exception:
            reflection = ""
        try:
            narrative_identity = asdict(identity.state)
        except Exception:
            narrative_identity = {}

    snap.identity_reflection = reflection[:2000]

    manifest_dict: dict[str, Any] | None = None
    try:
        from src.persistence.identity_manifest import IdentityManifestStore

        store = IdentityManifestStore()
        manifest_dict = asdict(store.manifest)
    except Exception:
        manifest_dict = None

    gestalt_dict = asdict(snap)
    pad = gestalt_dict.get("pad_state")
    if isinstance(pad, (list, tuple)):
        gestalt_dict["pad_state"] = [
            _finite_float(pad[0], 0.0),
            _finite_float(pad[1], 0.0),
            _finite_float(pad[2], 0.0),
        ]

    digest = str(getattr(memory, "experience_digest", "") or "")
    if len(digest) > 4000:
        digest = digest[:4000] + "…"

    ascription = ""
    if identity is not None:
        try:
            ascription = str(identity.ascription_line())
        except Exception:
            ascription = ""

    return {
        "schema": "sync_identity_v1",
        "gestalt": gestalt_dict,
        "identity_digest": digest,
        "identity_reflection": snap.identity_reflection,
        "ascription": ascription,
        "narrative_identity": narrative_identity,
        "identity_manifest": manifest_dict,
        "base_history": [_episode_stub(ep) for ep in tail],
    }
