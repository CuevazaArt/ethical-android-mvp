"""Versioned snapshot DTO for kernel persistence (JSON-serializable)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = 1


@dataclass
class KernelSnapshotV1:
    """
    Full serializable state needed to restore narrative continuity and calibration.

    Does not include: LLM session, WorkingMemory (STM), WebSocket handles.
    """

    schema_version: int = SCHEMA_VERSION

    # NarrativeMemory + identity
    episodes: List[Dict[str, Any]] = field(default_factory=list)
    narrative_counter: int = 0
    identity_state: Dict[str, Any] = field(default_factory=dict)

    # AlgorithmicForgiveness
    forgiveness_memories: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    forgiveness_cycle: int = 0
    forgiveness_recent_positives: int = 0

    # WeaknessPole
    weakness_type: str = "indecisive"
    weakness_base_intensity: Optional[float] = None
    weakness_records: List[Dict[str, Any]] = field(default_factory=list)
    weakness_cycle: int = 0

    # BayesianEngine
    bayesian_pruning_threshold: float = 0.3
    bayesian_gray_zone_threshold: float = 0.15
    bayesian_hypothesis_weights: List[float] = field(default_factory=lambda: [0.4, 0.35, 0.25])

    # LocusModule
    locus_alpha: float = 1.0
    locus_beta: float = 1.0
    locus_success_history: int = 0
    locus_failure_history: int = 0

    # VariabilityEngine
    variability_seed: Optional[int] = None
    variability_active: bool = True

    # Kernel auxiliary
    pruned_actions: Dict[str, List[str]] = field(default_factory=dict)

    # MockDAO (audit trail; participants/proposals stay default on fresh MockDAO)
    dao_record_counter: int = 0
    dao_records: List[Dict[str, Any]] = field(default_factory=list)
    dao_alerts: List[Dict[str, Any]] = field(default_factory=list)
