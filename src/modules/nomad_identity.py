"""
NomadIdentity — continuity bridge: checkpoint + immortality (no second identity model).

The kernel already implements **narrative persistence** and **ImmortalityProtocol**;
this module exposes a small **public summary** for APIs and docs alignment with
UNIVERSAL_ETHOS_AND_HUB.md and PROPUESTA_CONCIENCIA_NOMADA_HAL.md.
"""

from __future__ import annotations

from typing import Any


def nomad_identity_public(kernel: Any) -> dict[str, Any]:
    """Read-only snapshot for transparency payloads (best-effort)."""
    imm = getattr(kernel, "immortality", None)
    layers_info: dict[str, int] = {}
    if imm is not None and hasattr(imm, "layers"):
        try:
            layers_info = {k: len(v) for k, v in imm.layers.items()}
        except (TypeError, AttributeError):
            layers_info = {}
    out: dict[str, Any] = {
        "label": "NomadIdentity",
        "immortality_protocol_present": imm is not None,
        "immortality_layer_snapshots": layers_info,
        "note": "Identity continuity via NarrativeMemory + persistence + ImmortalityProtocol; see UNIVERSAL_ETHOS_AND_HUB.md",
    }
    hal = getattr(kernel, "_hal_context", None)
    if hal is not None and hasattr(hal, "to_public_dict"):
        out["hardware_context"] = hal.to_public_dict()
    return out
