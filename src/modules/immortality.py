"""
Immortality Protocol — Identity backup and restore.

Backup(G, θ) -> {DAO, Cloud, Local, Blockchain}
Restore(G, θ) -> NewKernel

Guarantees that the android's "soul" (narrative memory,
Bayesian parameters, forgiveness state, pole configuration)
survives total hardware destruction.

4 backup layers for cross-verification of integrity.
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Snapshot:
    """Complete capture of the soul's state."""
    id: str
    timestamp: str
    version: str

    # Narrative memory
    episodes_count: int
    last_episode_id: str

    # Bayesian parameters
    pruning_threshold: float
    hypothesis_weights: List[float]

    # Locus state
    alpha_locus: float
    beta_locus: float

    # Forgiveness state
    negative_load: float
    forgiven_memories: int

    # Weakness configuration
    weakness_type: str
    weakness_intensity: float
    emotional_load: float

    # Ethical poles
    pole_weights: Dict[str, float]

    # Integrity hash
    integrity_hash: str = ""


@dataclass
class RestoreResult:
    """Result of a restore operation."""
    success: bool
    source: str                    # "local", "cloud", "dao", "blockchain"
    snapshot_id: str
    integrity_verified: bool
    discrepancies: List[str]
    narrative: str


class ImmortalityProtocol:
    """
    Distributed backup and identity restoration system.

    4 backup layers:
    1. Local: fast snapshot for immediate restoration
    2. Cloud: full copy for physical disasters
    3. DAO: auditable records of decisions and morals
    4. Blockchain/IPFS: decentralized identity persistence

    Cross-verification: upon restore, the 4 copies are compared.
    If 2+ match, the majority is used.

    In MVP: everything is simulated in memory. In production: each layer
    would be a real external service.
    """

    def __init__(self):
        self.layers: Dict[str, List[Snapshot]] = {
            "local": [],
            "cloud": [],
            "dao": [],
            "blockchain": [],
        }
        self._snapshot_counter = 0

    def _calculate_hash(self, snapshot: Snapshot) -> str:
        """Calculates the integrity hash of the snapshot."""
        data = {
            "episodes": snapshot.episodes_count,
            "last_ep": snapshot.last_episode_id,
            "pruning_threshold": snapshot.pruning_threshold,
            "alpha": snapshot.alpha_locus,
            "beta": snapshot.beta_locus,
            "weakness": snapshot.weakness_type,
            "poles": snapshot.pole_weights,
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def backup(self, kernel) -> Snapshot:
        """
        Creates a complete snapshot of the kernel's state.
        Distributes it to all 4 backup layers.

        Args:
            kernel: EthicalKernel instance

        Returns:
            Created Snapshot
        """
        self._snapshot_counter += 1

        # Extract kernel state
        n_episodes = len(kernel.memory.episodes)
        last_ep = kernel.memory.episodes[-1].id if n_episodes > 0 else "none"

        # Algorithmic forgiveness
        neg_load = 0.0
        forgiven_count = 0
        if hasattr(kernel, 'forgiveness'):
            neg_load = kernel.forgiveness._negative_load()
            forgiven_count = sum(1 for m in kernel.forgiveness.memories.values() if m.forgiven)

        # Weakness pole
        weakness_t = "indecisive"
        weakness_int = 0.25
        emo_load = 0.0
        if hasattr(kernel, 'weakness'):
            weakness_t = kernel.weakness.type.value
            weakness_int = kernel.weakness.base_intensity
            emo_load = kernel.weakness.emotional_load()

        snapshot = Snapshot(
            id=f"SNAP-{self._snapshot_counter:04d}",
            timestamp=datetime.now().isoformat(),
            version="3.0",
            episodes_count=n_episodes,
            last_episode_id=last_ep,
            pruning_threshold=kernel.bayesian.pruning_threshold,
            hypothesis_weights=kernel.bayesian.hypothesis_weights.tolist(),
            alpha_locus=kernel.locus.alpha,
            beta_locus=kernel.locus.beta,
            negative_load=round(neg_load, 4),
            forgiven_memories=forgiven_count,
            weakness_type=weakness_t,
            weakness_intensity=weakness_int,
            emotional_load=round(emo_load, 4),
            pole_weights=dict(kernel.poles.base_weights),
        )

        snapshot.integrity_hash = self._calculate_hash(snapshot)

        # Distribute to all layers
        for layer in self.layers:
            self.layers[layer].append(snapshot)

        return snapshot

    def restore(self, kernel) -> RestoreResult:
        """
        Restores the kernel's state from backups.

        Process:
        1. Get the latest snapshot from each layer
        2. Cross-verify integrity (compare hashes)
        3. Use the snapshot with majority matches
        4. Apply state to the kernel

        Args:
            kernel: EthicalKernel instance to restore
        """
        # Get latest snapshots
        latest = {}
        for layer, snaps in self.layers.items():
            if snaps:
                latest[layer] = snaps[-1]

        if not latest:
            return RestoreResult(
                success=False, source="none", snapshot_id="",
                integrity_verified=False, discrepancies=["No snapshots available"],
                narrative="No backups available for restoration."
            )

        # Cross-verify integrity
        hashes = {layer: snap.integrity_hash for layer, snap in latest.items()}
        hash_counts = {}
        for h in hashes.values():
            hash_counts[h] = hash_counts.get(h, 0) + 1

        # Choose majority hash
        winning_hash = max(hash_counts, key=hash_counts.get)
        matches = hash_counts[winning_hash]
        total_layers = len(latest)

        # Find winning snapshot
        winning_source = None
        winning_snap = None
        for layer, snap in latest.items():
            if snap.integrity_hash == winning_hash:
                winning_source = layer
                winning_snap = snap
                break

        # Detect discrepancies
        discrepancies = []
        for layer, h in hashes.items():
            if h != winning_hash:
                discrepancies.append(
                    f"Layer '{layer}' has a different hash: possible tampering"
                )

        integrity_ok = matches >= 2  # At least 2 layers match

        # Apply restoration
        if integrity_ok and winning_snap:
            self._apply_snapshot(kernel, winning_snap)

        if integrity_ok:
            narrative = (
                f"Identity restored from '{winning_source}'. "
                f"Cross-verification: {matches}/{total_layers} layers match. "
                f"I am the same agent; my memory and purpose continue in this body."
            )
        else:
            narrative = (
                f"⚠ Restoration with compromised integrity. "
                f"Only {matches}/{total_layers} layers match. "
                f"Immediate DAO audit recommended."
            )

        return RestoreResult(
            success=integrity_ok,
            source=winning_source or "none",
            snapshot_id=winning_snap.id if winning_snap else "",
            integrity_verified=integrity_ok,
            discrepancies=discrepancies,
            narrative=narrative,
        )

    def _apply_snapshot(self, kernel, snapshot: Snapshot):
        """Applies a snapshot to the kernel."""
        import numpy as np

        kernel.bayesian.pruning_threshold = snapshot.pruning_threshold
        kernel.bayesian.hypothesis_weights = np.array(snapshot.hypothesis_weights)
        kernel.locus.alpha = snapshot.alpha_locus
        kernel.locus.beta = snapshot.beta_locus
        kernel.poles.base_weights = dict(snapshot.pole_weights)

    def last_backup(self) -> Optional[Snapshot]:
        """Returns the most recently created snapshot."""
        for layer in ["local", "cloud", "dao", "blockchain"]:
            if self.layers[layer]:
                return self.layers[layer][-1]
        return None

    def format_status(self) -> str:
        """Formats the immortality system status."""
        lines = ["  🔄 Immortality Protocol:"]
        for layer, snaps in self.layers.items():
            last = snaps[-1].id if snaps else "empty"
            lines.append(f"     {layer}: {len(snaps)} snapshots (last: {last})")

        last = self.last_backup()
        if last:
            lines.append(f"     Hash: {last.integrity_hash}")
            lines.append(f"     Episodes backed up: {last.episodes_count}")

        return "\n".join(lines)
