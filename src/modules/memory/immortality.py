"""
Immortality Protocol — Identity backup and restore.

Backup(G, θ) -> {DAO, Cloud, Local, Blockchain}
Restore(G, θ) -> NewKernel

Guarantees that the android's "soul" (narrative memory,
Bayesian parameters, forgiveness state, pole configuration,
and full NarrativeIdentityState) survives total hardware
destruction.

4 backup layers for cross-verification of integrity.

Gap closed (April 2026 — Antigravity): _apply_snapshot now
restores NarrativeIdentityTracker leans and core beliefs so
the Reflexive Mirror and Broken-Mirror logic survive restores.
"""
# Status: SCAFFOLD

import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Snapshot:
    """Complete capture of the soul's state."""

    id: str
    timestamp: str
    version: str

    # Narrative metadata
    episodes_count: int
    last_episode_id: str

    # Bayesian parameters
    pruning_threshold: float
    hypothesis_weights: list[float]

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
    pole_weights: dict[str, float]

    # Tier 3/4 Rich Narrative (with defaults)
    experience_digest: str = ""
    active_arc_id: str = ""
    integrity_hash: str = ""

    # NarrativeIdentityState — full self-model snapshot (April 2026)
    # Serialised as JSON string to keep Snapshot a plain dataclass.
    identity_state_json: str = "{}"


@dataclass
class RestoreResult:
    """Result of a restore operation."""

    success: bool
    source: str  # "local", "cloud", "dao", "blockchain"
    snapshot_id: str
    integrity_verified: bool
    discrepancies: list[str]
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

    def __init__(self, persistence_path: str | None = None) -> None:
        default_path = os.environ.get(
            "KERNEL_IMMORTALITY_BACKUP_PATH",
            "data/backups/immortality.json",
        )
        self.path = Path(persistence_path or default_path)
        self.layers: dict[str, list[Snapshot]] = {
            "local": [],
            "cloud": [],
            "dao": [],
            "blockchain": [],
        }
        self._snapshot_counter = 0
        self._load_local_backups()

    def _load_local_backups(self):
        """Loads snapshots from disk if they exist."""
        if not self.path.exists():
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
                for layer, snaps in data.items():
                    if layer in self.layers:
                        self.layers[layer] = [Snapshot(**s) for s in snaps]
                # Sync counter
                all_ids = []
                for snaps in self.layers.values():
                    for s in snaps:
                        try:
                            all_ids.append(int(s.id.split("-")[1]))
                        except (IndexError, ValueError):
                            pass
                if all_ids:
                    self._snapshot_counter = max(all_ids)
        except Exception:
            pass

    def _persist_local_backups(self):
        """Saves snapshots to disk using an atomic write pattern."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {layer: [snap.__dict__ for snap in snaps] for layer, snaps in self.layers.items()}

        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Atomic rename
            os.replace(temp_path, self.path)
        except Exception as e:
            if temp_path.exists():
                os.remove(temp_path)
            raise e

    def _calculate_hash(self, snapshot: Snapshot) -> str:
        """Calculates the integrity hash of the snapshot."""
        data = {
            "episodes": snapshot.episodes_count,
            "last_ep": snapshot.last_episode_id,
            "digest": snapshot.experience_digest,
            "arc": snapshot.active_arc_id,
            "pruning_threshold": snapshot.pruning_threshold,
            "alpha": snapshot.alpha_locus,
            "beta": snapshot.beta_locus,
            "weakness": snapshot.weakness_type,
            "poles": snapshot.pole_weights,
            # Identity state is included in hash so tampering is detectable
            "identity_state": snapshot.identity_state_json,
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def _serialize_identity_state(self, kernel) -> str:
        """Serialises the NarrativeIdentityState to a JSON string."""
        try:
            state = kernel.memory.identity.state
            payload = {
                "civic_lean": state.civic_lean,
                "care_lean": state.care_lean,
                "deliberation_lean": state.deliberation_lean,
                "careful_lean": state.careful_lean,
                "episode_count": state.episode_count,
                "core_beliefs": state.core_beliefs if state.core_beliefs else [],
            }
            return json.dumps(payload, ensure_ascii=False)
        except Exception:
            return "{}"

    def backup(self, kernel) -> Snapshot:
        """
        Creates a complete snapshot of the kernel's state.
        Distributes it to all 4 backup layers.

        Includes full NarrativeIdentityState (leans + core beliefs)
        so restores produce a fully coherent self-model.

        Args:
            kernel: EthicalKernel instance

        Returns:
            Created Snapshot
        """
        self._snapshot_counter += 1

        # Extract kernel state
        n_episodes = len(kernel.memory.episodes)
        last_ep = kernel.memory.episodes[-1].id if n_episodes > 0 else "none"
        digest = kernel.memory.experience_digest
        arc_id = kernel.memory.active_arc.id if kernel.memory.active_arc else "none"

        # Algorithmic forgiveness
        neg_load = 0.0
        forgiven_count = 0
        if hasattr(kernel, "forgiveness"):
            neg_load = kernel.forgiveness.total_negative_load()
            forgiven_count = sum(1 for m in kernel.forgiveness.memories.values() if m.forgiven)

        # Weakness pole
        weakness_t = "indecisive"
        weakness_int = 0.25
        emo_load = 0.0
        if hasattr(kernel, "weakness"):
            weakness_t = kernel.weakness.type.value
            weakness_int = kernel.weakness.base_intensity
            emo_load = kernel.weakness.emotional_load()

        # Mandatory Anti-NaN / Finitude hardening (Boy Scout)
        def _f(val: float, default: float = 0.5) -> float:
            return float(val) if math.isfinite(val) else default

        # Serialise the full NarrativeIdentityState (gap closed April 2026)
        identity_json = self._serialize_identity_state(kernel)

        snapshot = Snapshot(
            id=f"SNAP-{self._snapshot_counter:04d}",
            timestamp=datetime.now().isoformat(),
            version="3.2",
            episodes_count=n_episodes,
            last_episode_id=last_ep,
            experience_digest=digest,
            active_arc_id=arc_id,
            pruning_threshold=_f(kernel.bayesian.pruning_threshold),
            hypothesis_weights=[_f(w) for w in kernel.bayesian.hypothesis_weights.tolist()],
            alpha_locus=_f(kernel.locus.alpha),
            beta_locus=_f(kernel.locus.beta),
            negative_load=round(_f(neg_load, 0.0), 4),
            forgiven_memories=forgiven_count,
            weakness_type=weakness_t,
            weakness_intensity=_f(weakness_int),
            emotional_load=round(_f(emo_load, 0.0), 4),
            pole_weights={k: _f(v) for k, v in kernel.poles.base_weights.items()},
            identity_state_json=identity_json,
        )

        snapshot.integrity_hash = self._calculate_hash(snapshot)

        # Distribute to all layers
        for layer in self.layers:
            # In production, these would be separate services.
            # Here we simulate the distribution.
            self.layers[layer].append(snapshot)

        # Physical persistence for the 'local' and simulated state
        self._persist_local_backups()

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
                success=False,
                source="none",
                snapshot_id="",
                integrity_verified=False,
                discrepancies=["No snapshots available"],
                narrative="No backups available for restoration.",
            )

        # Cross-verify integrity
        hashes = {layer: snap.integrity_hash for layer, snap in latest.items()}
        hash_counts: dict[str, int] = {}
        for h in hashes.values():
            hash_counts[h] = hash_counts.get(h, 0) + 1

        # Choose majority hash
        winning_hash = max(hash_counts, key=lambda k: hash_counts[k])
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
                discrepancies.append(f"Layer '{layer}' has a different hash: possible tampering")

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
        """
        Applies a snapshot to the kernel.

        Restores:
        - Bayesian mixture weights and pruning threshold
        - Locus of control (alpha/beta)
        - Ethical pole base weights
        - Narrative digest and active arc pointer
        - Full NarrativeIdentityState: EMA leans + core beliefs
          (gap closed April 2026 — without this the Broken Mirror and
          Core Beliefs were lost after every hardware reset)
        """
        import numpy as np

        kernel.bayesian.pruning_threshold = snapshot.pruning_threshold
        kernel.bayesian.hypothesis_weights = np.array(snapshot.hypothesis_weights)
        kernel.locus.alpha = snapshot.alpha_locus
        kernel.locus.beta = snapshot.beta_locus
        kernel.poles.base_weights = dict(snapshot.pole_weights)

        # Restore narrative digest, active arc pointer, and identity state
        kernel.memory.experience_digest = snapshot.experience_digest
        if snapshot.active_arc_id != "none":
            active = next((a for a in kernel.memory.arcs if a.id == snapshot.active_arc_id), None)
            if active:
                kernel.memory.active_arc = active

        # Restore full NarrativeIdentityState (EMA leans + core beliefs)
        self._restore_identity_state(kernel, snapshot.identity_state_json)

    def _restore_identity_state(self, kernel, identity_json: str) -> None:
        """
        Deserialises and applies the NarrativeIdentityState from the snapshot.

        Gracefully handles missing keys (forward/backward compatibility).
        """
        if not identity_json or identity_json == "{}":
            return
        try:
            from src.modules.memory.narrative_identity import NarrativeIdentityState

            data = json.loads(identity_json)
            state = NarrativeIdentityState(
                civic_lean=data.get("civic_lean", 0.5),
                care_lean=data.get("care_lean", 0.5),
                deliberation_lean=data.get("deliberation_lean", 0.5),
                careful_lean=data.get("careful_lean", 0.5),
                episode_count=data.get("episode_count", 0),
                core_beliefs=data.get("core_beliefs", []),
            )
            kernel.memory.identity.import_state(state)
        except Exception:
            # Silent fail: worst case the tracker starts neutral, not corrupted
            pass

    def last_backup(self) -> Snapshot | None:
        """Returns the most recently created snapshot."""
        for layer in ["local", "cloud", "dao", "blockchain"]:
            if self.layers[layer]:
                return self.layers[layer][-1]
        return None

    def format_status(self) -> str:
        """Formats the immortality system status."""
        lines = ["  🔄 Immortality Protocol:"]
        for layer, snaps in self.layers.items():
            last_id = snaps[-1].id if snaps else "empty"
            lines.append(f"     {layer}: {len(snaps)} snapshots (last: {last_id})")

        last_snap = self.last_backup()
        if last_snap:
            lines.append(f"     Hash: {last_snap.integrity_hash}")
            lines.append(f"     Episodes backed up: {last_snap.episodes_count}")

        return "\n".join(lines)
