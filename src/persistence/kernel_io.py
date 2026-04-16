"""Extract / apply :class:`KernelSnapshotV1` without changing ethical algorithms."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from src.modules.forgiveness import WeightedMemory
from src.modules.judicial_escalation import EscalationPhase, strikes_threshold_from_env
from src.modules.metaplan_registry import MasterGoal
from src.modules.mock_dao import AuditRecord, SolidarityAlert
from src.modules.narrative_identity import NarrativeIdentityState
from src.modules.narrative_types import BodyState, HardwareProfile, NarrativeEpisode
from src.modules.skill_learning_registry import SkillLearningTicket, Status
from src.modules.subjective_time import SubjectiveClock
from src.modules.uchi_soto import interaction_profile_from_dict, interaction_profile_to_dict
from src.modules.user_model import (
    COGNITIVE_HOSTILE_ATTRIBUTION,
    COGNITIVE_NONE,
    COGNITIVE_PREMISE_RIGIDITY,
    COGNITIVE_URGENCY_AMPLIFICATION,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
)
from src.modules.variability import VariabilityConfig, VariabilityEngine
from src.modules.weakness_pole import WeaknessRecord, WeaknessType

from .schema import SCHEMA_VERSION, KernelSnapshotV1
from .snapshot_serde import (
    audit_record_to_dict,
    body_state_to_dict,
    episode_to_serializable_dict,
    master_goal_to_dict,
    narrative_identity_state_to_dict,
    solidarity_alert_to_dict,
    weighted_memory_to_dict,
)
from .snapshot_validate import validate_snapshot_for_apply

_ALLOWED_USER_MODEL_COGNITIVE = frozenset(
    {
        COGNITIVE_NONE,
        COGNITIVE_HOSTILE_ATTRIBUTION,
        COGNITIVE_PREMISE_RIGIDITY,
        COGNITIVE_URGENCY_AMPLIFICATION,
    }
)
_ALLOWED_USER_MODEL_RISK = frozenset({RISK_LOW, RISK_MEDIUM, RISK_HIGH})
_ALLOWED_USER_MODEL_JUDICIAL_PHASE = frozenset({""} | {p.value for p in EscalationPhase})


def _sanitize_user_model_cognitive(raw: str) -> str:
    x = (raw or "").strip()[:64]
    return x if x in _ALLOWED_USER_MODEL_COGNITIVE else COGNITIVE_NONE


def _sanitize_user_model_risk(raw: str) -> str:
    x = (raw or "").strip()[:32]
    return x if x in _ALLOWED_USER_MODEL_RISK else RISK_LOW


def _sanitize_user_model_judicial_phase(raw: str) -> str:
    x = (raw or "").strip()[:64]
    return x if x in _ALLOWED_USER_MODEL_JUDICIAL_PHASE else ""


if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def _finite_float(val: Any, field: str) -> float:
    try:
        x = float(val)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Kernel snapshot field {field} is not numeric: {val!r}") from e
    if not math.isfinite(x):
        raise ValueError(f"Kernel snapshot field {field} must be finite: {val!r}")
    return x


def episode_to_dict(ep: NarrativeEpisode) -> dict[str, Any]:
    """Backward-compatible name; see :func:`~src.persistence.snapshot_serde.episode_to_serializable_dict`."""
    return episode_to_serializable_dict(ep)


def episode_from_dict(d: dict[str, Any]) -> NarrativeEpisode:
    bs_dict = d["body_state"]
    # Handle older snapshots without the new fields
    hp_str = bs_dict.get("hardware_profile", "android")
    try:
        hp = HardwareProfile(hp_str)
    except ValueError:
        hp = HardwareProfile.ANDROID

    body = BodyState(
        energy=bs_dict.get("energy", 1.0),
        active_nodes=bs_dict.get("active_nodes", 8),
        sensors_ok=bs_dict.get("sensors_ok", True),
        description=bs_dict.get("description", ""),
        hardware_profile=hp,
        hardware_id=bs_dict.get("hardware_id", "default_body_01"),
        capabilities=list(bs_dict.get("capabilities", [])),
    )
    pad = tuple(d["affect_pad"]) if d.get("affect_pad") is not None else None
    return NarrativeEpisode(
        id=d["id"],
        timestamp=d["timestamp"],
        place=d["place"],
        event_description=d["event_description"],
        body_state=body,
        action_taken=d["action_taken"],
        morals=dict(d["morals"]),
        verdict=d["verdict"],
        ethical_score=_finite_float(d.get("ethical_score"), "episode.ethical_score"),
        decision_mode=d["decision_mode"],
        sigma=_finite_float(d.get("sigma"), "episode.sigma"),
        context=d["context"],
        affect_pad=pad,
        affect_weights=dict(d["affect_weights"]) if d.get("affect_weights") is not None else None,
    )


def extract_snapshot(kernel: EthicalKernel) -> KernelSnapshotV1:
    """Serialize mutable kernel state into a versioned snapshot."""
    mem = kernel.memory
    fg = kernel.forgiveness
    w = kernel.weakness
    dao = kernel.dao
    dao_st = dao.export_state()

    return KernelSnapshotV1(
        schema_version=SCHEMA_VERSION,
        episodes=[episode_to_dict(ep) for ep in mem.episodes],
        narrative_counter=mem._counter,
        identity_state=narrative_identity_state_to_dict(mem.identity.state),
        experience_digest=getattr(mem, "experience_digest", "") or "",
        forgiveness_memories={k: weighted_memory_to_dict(v) for k, v in fg.memories.items()},
        forgiveness_cycle=fg._cycle,
        forgiveness_recent_positives=fg._recent_positives,
        weakness_type=w.type.value,
        weakness_base_intensity=w.base_intensity,
        weakness_records=[
            {
                "episode_id": r.episode_id,
                "type": r.type.value,
                "intensity": r.intensity,
                "timestamp": r.timestamp,
            }
            for r in w.records
        ],
        weakness_cycle=w._cycle,
        bayesian_pruning_threshold=kernel.bayesian.pruning_threshold,
        bayesian_gray_zone_threshold=kernel.bayesian.gray_zone_threshold,
        bayesian_hypothesis_weights=[float(x) for x in kernel.bayesian.hypothesis_weights],
        locus_alpha=kernel.locus.alpha,
        locus_beta=kernel.locus.beta,
        locus_success_history=kernel.locus.success_history,
        locus_failure_history=kernel.locus.failure_history,
        variability_seed=kernel.var_engine.config.seed,
        variability_active=kernel.var_engine._active,
        pruned_actions=dict(kernel._pruned_actions),
        dao_record_counter=dao._record_counter,
        dao_records=[audit_record_to_dict(r) for r in dao.records],
        dao_alerts=[solidarity_alert_to_dict(a) for a in dao.alerts],
        constitution_l1_drafts=list(getattr(kernel, "constitution_l1_drafts", []) or []),
        constitution_l2_drafts=list(getattr(kernel, "constitution_l2_drafts", []) or []),
        dao_proposal_counter=dao_st["proposal_counter"],
        dao_participants=dao_st["participants"],
        dao_proposals=dao_st["proposals"],
        metaplan_goals=[master_goal_to_dict(g) for g in kernel.metaplan.goals()],
        somatic_marker_weights=dict(kernel.somatic_store._negative_weights),
        skill_learning_tickets=[
            {
                "id": t.id,
                "scope_description": t.scope_description,
                "justification": t.justification,
                "status": t.status,
            }
            for t in kernel.skill_learning._tickets
        ],
        user_model_frustration_streak=int(kernel.user_model.frustration_streak),
        user_model_premise_concern_streak=int(kernel.user_model.premise_concern_streak),
        user_model_last_circle=str(kernel.user_model.last_circle)[:120],
        user_model_turns_observed=int(kernel.user_model.turns_observed),
        user_model_cognitive_pattern=str(kernel.user_model.cognitive_pattern)[:64],
        user_model_risk_band=str(kernel.user_model.risk_band)[:32],
        user_model_judicial_phase=str(kernel.user_model.judicial_phase or "")[:64],
        subjective_turn_index=int(kernel.subjective_clock.turn_index),
        subjective_stimulus_ema=float(kernel.subjective_clock.stimulus_ema),
        escalation_session_strikes=int(kernel.escalation_session.strikes),
        escalation_session_idle_turns=int(kernel.escalation_session.idle_turns),
        uchi_soto_profiles=[
            interaction_profile_to_dict(p) for p in kernel.uchi_soto.profiles.values()
        ],
        migratory_body=body_state_to_dict(kernel.migration.current_body),
    )


def apply_snapshot(kernel: EthicalKernel, snap: KernelSnapshotV1) -> None:
    """Restore mutable state. Validates against JSON Schema before mutating the kernel."""
    validate_snapshot_for_apply(snap)

    mem = kernel.memory
    mem.episodes = [episode_from_dict(e) for e in snap.episodes]
    mem._counter = snap.narrative_counter
    mem.identity.state = NarrativeIdentityState(**snap.identity_state)
    mem.experience_digest = snap.experience_digest or ""

    fg = kernel.forgiveness
    fg.memories = {k: WeightedMemory(**v) for k, v in snap.forgiveness_memories.items()}
    fg._cycle = snap.forgiveness_cycle
    fg._recent_positives = snap.forgiveness_recent_positives

    w = kernel.weakness
    w.type = WeaknessType(snap.weakness_type)
    if snap.weakness_base_intensity is not None:
        w.base_intensity = snap.weakness_base_intensity
    w.records = [
        WeaknessRecord(
            episode_id=r["episode_id"],
            type=WeaknessType(r["type"]),
            intensity=_finite_float(r.get("intensity"), "weakness_record.intensity"),
            timestamp=_finite_float(r.get("timestamp"), "weakness_record.timestamp"),
        )
        for r in snap.weakness_records
    ]
    w._cycle = snap.weakness_cycle

    kernel.bayesian.pruning_threshold = _finite_float(
        snap.bayesian_pruning_threshold, "bayesian_pruning_threshold"
    )
    kernel.bayesian.gray_zone_threshold = _finite_float(
        snap.bayesian_gray_zone_threshold, "bayesian_gray_zone_threshold"
    )
    hw_list = [
        _finite_float(x, f"bayesian_hypothesis_weights[{i}]")
        for i, x in enumerate(snap.bayesian_hypothesis_weights)
    ]
    kernel.bayesian.hypothesis_weights = np.array(hw_list, dtype=float)

    lo = kernel.locus
    lo.alpha = max(lo.ALPHA_MIN, min(lo.ALPHA_MAX, snap.locus_alpha))
    lo.beta = max(lo.BETA_MIN, min(lo.BETA_MAX, snap.locus_beta))
    kernel.locus.success_history = snap.locus_success_history
    kernel.locus.failure_history = snap.locus_failure_history

    cfg = VariabilityConfig(seed=snap.variability_seed)
    engine = VariabilityEngine(cfg)
    if not snap.variability_active:
        engine.deactivate()
    kernel.var_engine = engine
    kernel.bayesian.variability = engine

    kernel._pruned_actions = dict(snap.pruned_actions)

    dao = kernel.dao
    dao._record_counter = snap.dao_record_counter
    dao.records = [AuditRecord(**r) for r in snap.dao_records]
    dao.alerts = [SolidarityAlert(**a) for a in snap.dao_alerts]
    dao.import_state(
        {
            "proposal_counter": snap.dao_proposal_counter,
            "participants": snap.dao_participants,
            "proposals": snap.dao_proposals,
        }
    )

    kernel.constitution_l1_drafts = list(snap.constitution_l1_drafts or [])
    kernel.constitution_l2_drafts = list(snap.constitution_l2_drafts or [])

    mp: list[MasterGoal] = []
    for g in snap.metaplan_goals or []:
        try:
            mp.append(
                MasterGoal(
                    id=str(g.get("id", "")),
                    title=str(g.get("title", ""))[:500],
                    priority=float(g.get("priority", 0.5)),
                )
            )
        except (TypeError, ValueError):
            continue
    kernel.metaplan.replace_goals(mp)

    kernel.somatic_store.replace_weights(dict(snap.somatic_marker_weights or {}))

    tickets: list[SkillLearningTicket] = []
    for t in snap.skill_learning_tickets or []:
        try:
            st = cast(Status, str(t.get("status", "pending")))
            tickets.append(
                SkillLearningTicket(
                    id=str(t.get("id", "")),
                    scope_description=str(t.get("scope_description", ""))[:2000],
                    justification=str(t.get("justification", ""))[:4000],
                    status=st,
                )
            )
        except (TypeError, ValueError):
            continue
    kernel.skill_learning.replace_tickets(tickets)

    um = kernel.user_model
    um.frustration_streak = max(0, min(24, int(snap.user_model_frustration_streak)))
    um.premise_concern_streak = max(0, min(16, int(snap.user_model_premise_concern_streak)))
    um.last_circle = str(snap.user_model_last_circle or "neutral_soto")[:120]
    um.turns_observed = max(0, int(snap.user_model_turns_observed))

    kernel.subjective_clock = SubjectiveClock(
        turn_index=max(0, int(snap.subjective_turn_index)),
        stimulus_ema=max(0.0, min(1.0, float(snap.subjective_stimulus_ema))),
    )

    kernel.escalation_session.strikes = max(0, min(500, int(snap.escalation_session_strikes)))
    kernel.escalation_session.idle_turns = max(0, min(100, int(snap.escalation_session_idle_turns)))

    um.cognitive_pattern = _sanitize_user_model_cognitive(snap.user_model_cognitive_pattern)
    um.risk_band = _sanitize_user_model_risk(snap.user_model_risk_band)
    um.judicial_phase = _sanitize_user_model_judicial_phase(snap.user_model_judicial_phase)
    um.note_judicial_escalation(
        kernel.escalation_session.strikes,
        strikes_threshold_from_env(),
    )

    kernel.uchi_soto.profiles = {}
    for row in snap.uchi_soto_profiles or []:
        if not isinstance(row, dict):
            continue
        try:
            prof = interaction_profile_from_dict(row)
            kernel.uchi_soto.profiles[prof.agent_id] = prof
        except (TypeError, ValueError):
            continue

    # Block 4.3 — Migratory Body Restore
    mb = snap.migratory_body
    if mb:
        hp_str = mb.get("hardware_profile", "android")
        try:
            hp = HardwareProfile(hp_str)
        except ValueError:
            hp = HardwareProfile.ANDROID

        kernel.migration.current_body = BodyState(
            energy=mb.get("energy", 1.0),
            active_nodes=mb.get("active_nodes", 8),
            sensors_ok=mb.get("sensors_ok", True),
            description=mb.get("description", ""),
            hardware_profile=hp,
            hardware_id=mb.get("hardware_id", "default_body_01"),
            capabilities=list(mb.get("capabilities", [])),
        )
