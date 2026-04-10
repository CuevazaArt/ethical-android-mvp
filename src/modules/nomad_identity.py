"""
NomadIdentity — continuity bridge: checkpoint + immortality (no second identity model).

The kernel already implements **narrative persistence** and **ImmortalityProtocol**;
this module exposes a small **public summary** for APIs and docs alignment with
UNIVERSAL_ETHOS_AND_HUB.md.
"""

from __future__ import annotations

from typing import Any, Dict


def nomad_identity_public(kernel: Any) -> Dict[str, Any]:
    """Read-only snapshot for transparency payloads (best-effort)."""
    imm = getattr(kernel, "immortality", None)
    layers_info: Dict[str, int] = {}
    if imm is not None and hasattr(imm, "layers"):
        try:
            layers_info = {k: len(v) for k, v in imm.layers.items()}
        except (TypeError, AttributeError):
            layers_info = {}
    return {
        "label": "NomadIdentity",
        "immortality_protocol_present": imm is not None,
        "immortality_layer_snapshots": layers_info,
        "note": "Identity continuity via NarrativeMemory + persistence + ImmortalityProtocol; see UNIVERSAL_ETHOS_AND_HUB.md",
    }
