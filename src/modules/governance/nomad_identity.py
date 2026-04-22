from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class PeerReputation:
    """Reputation metrics for a peer node in the nomadic swarm."""

    node_id: str
    trust_score: float = 0.5  # [0, 1]
    last_interaction: str = field(default_factory=lambda: datetime.now().isoformat())
    interaction_count: int = 0
    tags: list[str] = field(default_factory=list)


class NomadicRegistry:
    """
    Registry for peer nodes encountered during nomadic deployment. (V12.1)
    """

    def __init__(self):
        self.peers: dict[str, PeerReputation] = {}

    def register_peer(self, node_id: str, delta_trust: float = 0.0):
        """Updates or registers a peer node's trust score."""
        if node_id not in self.peers:
            self.peers[node_id] = PeerReputation(node_id)
            _log.info("NomadicRegistry: New peer registered: %s", node_id)

        p = self.peers[node_id]
        p.trust_score = max(0.0, min(1.0, p.trust_score + delta_trust))
        p.last_interaction = datetime.now().isoformat()
        p.interaction_count += 1

    def get_peer_trust(self, node_id: str) -> float:
        """Returns trust score; defaults to 0.5 for strangers."""
        return self.peers.get(node_id, PeerReputation(node_id)).trust_score


def nomad_identity_public(kernel: Any) -> dict[str, Any]:
    """Read-only snapshot for transparency payloads (best-effort)."""
    imm = getattr(kernel, "immortality", None)
    registry = getattr(kernel, "nomadic_registry", None)

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
        "swarm_peers_count": len(registry.peers) if registry else 0,
        "note": "Identity continuity via NarrativeMemory + persistence + ImmortalityProtocol; see UNIVERSAL_ETHOS_AND_HUB.md",
    }

    hal = getattr(kernel, "_hal_context", None)
    if hal is not None and hasattr(hal, "to_public_dict"):
        out["hardware_context"] = hal.to_public_dict()
    return out
