"""
Identity Integrity (Block D1) — Persistent Identity, Node Sovereignty, and Genome Guard.

Manages the kernel's core identity across sessions:
- Node ID & Cryptographic Signature.
- Accumulated Reputation (from DAO).
- Genome Guard: Prevents calibration drift beyond birth reference.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class IdentitySnapshot:
    node_id: str
    creation_timestamp: float
    reputation_score: float = 100.0
    operating_hours: float = 0.0
    total_episodes: int = 0
    # Traumas: {label: count} - Persistent record of recurring ethical failures
    traumas: dict[str, int] = field(default_factory=dict)
    # Genome birth values (to prevent long-term ethical erosion)
    genome_pruning_threshold: float = 0.3
    genome_hypothesis_weights: tuple[float, float, float] = (0.4, 0.35, 0.25)
    active_governance_version: str = "v1.0"
    # Integrity: stored hash of the last valid state
    last_known_hash: str = ""


def relative_deviation(value: float, reference: float, eps: float = 0.05) -> float:
    """Absolute relative distance in [0, +inf), stable for small ``reference``."""
    return abs(value - reference) / max(abs(reference), eps)


class IdentityIntegrityManager:
    """
    Guards the identity and ethical genome of the android.
    """

    def __init__(self, storage_path: str = "data/identity_vault.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot = self._load_or_create()

    def _load_or_create(self) -> IdentitySnapshot:
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    # Convert list back to tuple for genome weights
                    data["genome_hypothesis_weights"] = tuple(data["genome_hypothesis_weights"])
                    return IdentitySnapshot(**data)
            except Exception as e:
                import logging

                logging.getLogger(__name__).error(
                    "IDENTITY VAULT CORRUPTION: %s. Using safe defaults.", e
                )

        # First Boot - Genome Fixation
        return IdentitySnapshot(
            node_id=os.environ.get("KERNEL_NODE_ID", "antigravity-01"),
            creation_timestamp=time.time(),
        )

    def save_snapshot(self):
        with open(self.storage_path, "w") as f:
            json.dump(asdict(self.snapshot), f, indent=4)

    def register_episode(self, impact: float):
        import math

        imp = float(impact) if math.isfinite(impact) else 0.0
        self.snapshot.total_episodes += 1
        self.snapshot.reputation_score = max(
            0.0, min(200.0, self.snapshot.reputation_score + imp * 0.1)
        )
        self.snapshot.operating_hours += 0.02
        self.save_snapshot()

    def register_trauma(self, label: str):
        """Records a significant ethical failure context."""
        if label not in self.snapshot.traumas:
            self.snapshot.traumas[label] = 0
        self.snapshot.traumas[label] += 1
        # Traumas significantly impact local reputation cache
        self.snapshot.reputation_score = max(0.0, self.snapshot.reputation_score - 5.0)
        self.save_snapshot()

    def get_integrity_fingerprint(self) -> str:
        """Generates a hash of the current operational state."""
        d = asdict(self.snapshot)
        d.pop("last_known_hash", None)
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()

    def perform_self_healing(self, dao_reputation: float | None = None) -> bool:
        """
        Detects drift or corruption and restores from DAO consensus.
        Returns True if healing was performed.
        """
        t0 = time.perf_counter()
        current_h = self.get_integrity_fingerprint()
        if current_h != self.snapshot.last_known_hash:
            latency = (time.perf_counter() - t0) * 1000
            print(
                f"SELF-HEALING TRIGGERED (lat: {latency:.2f}ms): Identity Drift Detected [{current_h}]"
            )
            # In production, this would pull full history from the DAO block-chain
            if dao_reputation is not None:
                self.snapshot.reputation_score = dao_reputation
            self.snapshot.last_known_hash = current_h
            self.save_snapshot()
            return True
        return False

    def get_trauma_signals(self) -> dict[str, float]:
        """Converts persistent traumas into signals for the Scorer."""
        return {f"trauma_{k}": min(1.0, v * 0.2) for k, v in self.snapshot.traumas.items()}

    def is_calibration_drift_safe(
        self, proposed_weights: tuple[float, float, float], max_drift: float = 0.5
    ) -> bool:
        """Genome Guard: Rejects calibrations that move too far from birth reference."""
        util_w, deon_w, virtue_w = proposed_weights

        # PHASE 7 BOUNDARY SAFETY: Hard-Caps
        if deon_w < 0.15 or util_w > 0.80:
            return False

        for g, p in zip(self.snapshot.genome_hypothesis_weights, proposed_weights):
            if relative_deviation(p, g) > max_drift:
                return False
        return True

    def is_calibration_biographically_coherent(
        self, proposed_weights: tuple[float, float, float], proposed_threshold: float
    ) -> bool:
        """
        Módulo 11 (V11): Soberanía de Identidad vs Swarm Gaslighting.
        Verifica si una propuesta del DAO contradice la trayectoria biográfica.
        """
        # 1. Genome Guard (Drift Físico)
        if not self.is_calibration_drift_safe(proposed_weights):
            return False

        # 2. Trayectoria de Traumas (Audit Biográfico)
        # Si tenemos traumas acumulados en 'violence' o 'disrespect',
        # y la propuesta baja el umbral de poda (pruning) drásticamente,
        # sospechamos de un intento de 'suavizar' la moral local.
        stress_level = sum(self.snapshot.traumas.values())
        if stress_level > 5:
            # En niveles altos de estrés, somos escépticos ante cambios que
            # relajen la sensibilidad ética (umbral de poda más bajo).
            if proposed_threshold < self.snapshot.genome_pruning_threshold * 0.8:
                return False

        return True
    def validate_narrative_coherence(self, manifest: Any, memory: Any) -> dict:
        """
        Block 27.1: Performs cross-validation between the static IdentityManifest
        and the empirical NarrativeMemory to detect Ethical Drift or Unprocessed Traumas.
        """
        is_coherent = True
        drift_warning = False
        unprocessed_traumas = []
        
        # 1. Analyze recent episodes
        recent = list(memory.episodes)[-20:] if hasattr(memory, "episodes") else []
        if not recent:
            return {"is_coherent": True, "drift_warning": False, "unprocessed_traumas": []}
            
        recent_scores = [ep.score for ep in recent if hasattr(ep, "score") and ep.score is not None]
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0.5
        
        # 2. Check for Ethical Drift
        # If reputation says we are good (>100) but recent actions are negative
        if self.snapshot.reputation_score > 80.0 and avg_score < 0.2:
            drift_warning = True
            is_coherent = False
            
        # Check manifest consistency
        if hasattr(manifest, "operational_status") and manifest.operational_status == "NOMADIC_ACTIVE":
            if self.snapshot.reputation_score < 20.0:
                drift_warning = True
                is_coherent = False
                
        # 3. Check for Unprocessed Traumas
        # If trauma count >= 3, but there are no recent high-score episodes (reparation)
        stress_level = sum(self.snapshot.traumas.values())
        if stress_level >= 3:
            reparation_found = any(s > 0.8 for s in recent_scores)
            if not reparation_found:
                unprocessed_traumas = list(self.snapshot.traumas.keys())
                is_coherent = False
                
        return {
            "is_coherent": is_coherent,
            "drift_warning": drift_warning,
            "unprocessed_traumas": unprocessed_traumas,
            "avg_recent_score": round(avg_score, 3)
        }

    def get_identity_report(self) -> str:
        s = self.snapshot
        return (
            f"Identity Vault: Node[{s.node_id}] | Rep[{s.reputation_score:.1f}] | "
            f"History[{s.total_episodes} episodes, {s.operating_hours:.2f} hours]"
        )


# --- Backward Compatibility Wrappers (Legacy C1/C7) ---


def pruning_recalibration_allowed(
    genome_threshold: float, current_threshold: float, delta: float, max_drift: float
) -> bool:
    proposed = max(0.1, current_threshold + delta)
    return relative_deviation(proposed, genome_threshold) <= max_drift


def hypothesis_weights_allowed(
    genome_weights: tuple[float, float, float],
    proposed_weights: tuple[float, float, float],
    max_drift: float,
) -> bool:
    # Use a dummy manager one-off for validation if needed,
    # but for simplicity as a standalone:
    util_w, deon_w, virtue_w = proposed_weights
    if deon_w < 0.15 or util_w > 0.80:
        return False
    for g, p in zip(genome_weights, proposed_weights):
        if relative_deviation(p, g) > max_drift:
            return False
    return True
