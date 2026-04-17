"""
Swarm Oracle (I4) — Persistence for peer reputation and session hints.

Maintains a local cache of discovered peers, their voting history, and
reputation scores to enable cross-session trust even in disconnected (offline) modes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class PeerEntry:
    node_id: str
    last_seen: float
    reputation: float = 1.0  # [0, 1]
    confirmed_witnesses: int = 0

class SwarmOracle:
    """
    Persistence layer for swarm metadata.
    """
    def __init__(self, cache_path: str = "config/swarm_cache.json"):
        self.cache_path = Path(cache_path)
        self.peers: dict[str, PeerEntry] = {}
        self.load()

    def load(self):
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.peers[k] = PeerEntry(**v)
            except Exception:
                pass # Degrade gracefully if JSON is corrupt

    def save(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump({k: asdict(v) for k, v in self.peers.items()}, f, indent=2)

    def register_interaction(self, node_id: str, success: bool):
        now = __import__("time").time()
        if node_id not in self.peers:
            self.peers[node_id] = PeerEntry(node_id=node_id, last_seen=now)
        
        peer = self.peers[node_id]
        peer.last_seen = now
        if success:
            peer.reputation = min(1.0, peer.reputation + 0.05)
            peer.confirmed_witnesses += 1
        else:
            peer.reputation = max(0.0, peer.reputation - 0.1)
        
        self.save()

    def get_reputation_hint(self, node_id: str) -> float:
        return self.peers.get(node_id, PeerEntry(node_id, 0, 0.5)).reputation

    def apply_slashing(self, node_id: str, penalty: float = 0.2):
        """
        Bloque 7.2: Forceful reputation penalty for nodes that provide false verification.
        """
<<<<<<< HEAD
        if node_id not in self.peers:
            # Register unknown peer with default 0.5 before slashing
            now = __import__("time").time()
            self.peers[node_id] = PeerEntry(node_id=node_id, last_seen=now, reputation=0.5)
            
        peer = self.peers[node_id]
        peer.reputation = max(0.0, peer.reputation - severity)
        self.save()

    def process_forgiveness_pulse(self, forgiveness_rate: float = 0.02):
        """
        Algorithmic Forgiveness (I2): Slowly nudge reputations back toward baseline (0.5).
        Prevents permanent 'ghosting' of nodes that made past errors.
        """
        for peer in self.peers.values():
            if peer.reputation < 0.5:
                # Recovery
                peer.reputation = min(0.5, peer.reputation + forgiveness_rate)
            elif peer.reputation > 0.5:
                # Normalization (optional)
                pass 
        self.save()
=======
        if node_id in self.peers:
            peer = self.peers[node_id]
            peer.reputation = max(0.0, peer.reputation - severity)
            self.save()
>>>>>>> origin/master-Cursor
