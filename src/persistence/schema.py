"""Versioned snapshot DTO for kernel persistence (JSON-serializable)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = 4


@dataclass
class KernelSnapshotV1:
    """
    Full serializable state needed to restore narrative continuity and calibration.

    Does not include: LLM session, WorkingMemory (STM), WebSocket handles.
    """

    schema_version: int = SCHEMA_VERSION

    # NarrativeMemory + identity
    episodes: list[dict[str, Any]] = field(default_factory=list)
    narrative_counter: int = 0
    identity_state: dict[str, Any] = field(default_factory=dict)
    experience_digest: str = ""

    # AlgorithmicForgiveness
    forgiveness_memories: dict[str, dict[str, Any]] = field(default_factory=dict)
    forgiveness_cycle: int = 0
    forgiveness_recent_positives: int = 0

    # WeaknessPole
    weakness_type: str = "indecisive"
    weakness_base_intensity: float | None = None
    weakness_records: list[dict[str, Any]] = field(default_factory=list)
    weakness_cycle: int = 0

    # BayesianEngine
    bayesian_pruning_threshold: float = 0.3
    bayesian_gray_zone_threshold: float = 0.15
    bayesian_hypothesis_weights: list[float] = field(default_factory=lambda: [0.4, 0.35, 0.25])

    # LocusModule
    locus_alpha: float = 1.0
    locus_beta: float = 1.0
    locus_success_history: int = 0
    locus_failure_history: int = 0

    # VariabilityEngine
    variability_seed: int | None = None
    variability_active: bool = True

    # Kernel auxiliary
    pruned_actions: dict[str, list[str]] = field(default_factory=dict)

    # MockDAO (audit trail + V12.3 serialized proposals/participants)
    dao_record_counter: int = 0
    dao_records: list[dict[str, Any]] = field(default_factory=list)
    dao_alerts: list[dict[str, Any]] = field(default_factory=list)

    # V12.2 — DemocraticBuffer drafts (L1/L2 only; L0 remains in buffer.py)
    constitution_l1_drafts: list[dict[str, Any]] = field(default_factory=list)
    constitution_l2_drafts: list[dict[str, Any]] = field(default_factory=list)

    # V12.3 — MockDAO proposals + participants (off-chain quadratic voting state)
    dao_proposal_counter: int = 0
    dao_participants: list[dict[str, Any]] = field(default_factory=list)
    dao_proposals: list[dict[str, Any]] = field(default_factory=list)

    # Vertical Phase 2 — v10 advisory memory (tone only; does not change MalAbs / Bayes)
    metaplan_goals: list[dict[str, Any]] = field(default_factory=list)
    somatic_marker_weights: dict[str, float] = field(default_factory=dict)
    skill_learning_tickets: list[dict[str, Any]] = field(default_factory=list)

    # v7 relational + subjective time (checkpoint continuity; WorkingMemory STM still not persisted)
    user_model_frustration_streak: int = 0
    user_model_premise_concern_streak: int = 0
    user_model_last_circle: str = "neutral_soto"
    user_model_turns_observed: int = 0
    user_model_cognitive_pattern: str = "none"
    user_model_risk_band: str = "low"
    user_model_judicial_phase: str = ""
    subjective_turn_index: int = 0
    subjective_stimulus_ema: float = 0.55

    # V11 judicial escalation session (advisory; checkpoint continuity)
    escalation_session_strikes: int = 0
    escalation_session_idle_turns: int = 0

    # Uchi–Soto per-agent profiles (tone + trust continuity; advisory)
    uchi_soto_profiles: list[dict[str, Any]] = field(default_factory=list)

    # Block 4.3 — Migratory Body
    migratory_body: dict[str, Any] = field(default_factory=dict)
