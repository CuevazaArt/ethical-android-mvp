"""
Explicit JSON-serializable mapping for :class:`~src.persistence.schema.KernelSnapshotV1`.

Avoids :func:`dataclasses.asdict` on the snapshot root so persisted field sets stay deliberate
and documented alongside ``schemas/kernel_snapshot_v3.schema.json``.
"""

from __future__ import annotations

from typing import Any

from src.modules.metaplan_registry import MasterGoal
from src.modules.mock_dao import AuditRecord, SolidarityAlert

from .schema import KernelSnapshotV1


def body_state_to_dict(bs: Any) -> dict[str, Any]:
    """Serialize :class:`~src.modules.narrative_types.BodyState` (explicit fields)."""
    return {
        "energy": float(bs.energy),
        "active_nodes": int(bs.active_nodes),
        "sensors_ok": bool(bs.sensors_ok),
        "description": str(bs.description or ""),
        "hardware_profile": bs.hardware_profile.value
        if hasattr(bs, "hardware_profile")
        else "android",
        "hardware_id": str(getattr(bs, "hardware_id", "default_body_01")),
        "capabilities": list(getattr(bs, "capabilities", [])),
    }


def episode_to_serializable_dict(ep: Any) -> dict[str, Any]:
    """Serialize :class:`~src.modules.narrative.NarrativeEpisode` without root ``asdict``."""
    d: dict[str, Any] = {
        "id": ep.id,
        "timestamp": ep.timestamp,
        "place": ep.place,
        "event_description": ep.event_description,
        "body_state": body_state_to_dict(ep.body_state),
        "action_taken": ep.action_taken,
        "morals": dict(ep.morals),
        "verdict": ep.verdict,
        "ethical_score": float(ep.ethical_score),
        "decision_mode": ep.decision_mode,
        "sigma": float(ep.sigma),
        "context": ep.context,
    }
    if ep.affect_pad is not None:
        d["affect_pad"] = [float(x) for x in ep.affect_pad]
    if ep.affect_weights is not None:
        d["affect_weights"] = {str(k): float(v) for k, v in ep.affect_weights.items()}
    return d


def narrative_identity_state_to_dict(state: Any) -> dict[str, Any]:
    """Serialize :class:`~src.modules.narrative_identity.NarrativeIdentityState`."""
    return {
        "civic_lean": float(state.civic_lean),
        "care_lean": float(state.care_lean),
        "deliberation_lean": float(state.deliberation_lean),
        "careful_lean": float(state.careful_lean),
        "episode_count": int(state.episode_count),
    }


def weighted_memory_to_dict(mem: Any) -> dict[str, Any]:
    """Serialize :class:`~src.modules.forgiveness.WeightedMemory`."""
    return {
        "episode_id": mem.episode_id,
        "original_score": float(mem.original_score),
        "current_weight": float(mem.current_weight),
        "age_cycles": int(mem.age_cycles),
        "type": mem.type,
        "context": mem.context,
        "forgiven": bool(mem.forgiven),
    }


def audit_record_to_dict(r: AuditRecord) -> dict[str, Any]:
    """Serialize :class:`~src.modules.mock_dao.AuditRecord` (DAO audit line)."""
    out: dict[str, Any] = {
        "id": r.id,
        "type": r.type,
        "content": r.content,
        "timestamp": r.timestamp,
    }
    if r.episode_id is not None:
        out["episode_id"] = r.episode_id
    return out


def solidarity_alert_to_dict(a: SolidarityAlert) -> dict[str, Any]:
    """Serialize :class:`~src.modules.mock_dao.SolidarityAlert`."""
    return {
        "type": a.type,
        "location": a.location,
        "radius_meters": int(a.radius_meters),
        "message": a.message,
        "timestamp": a.timestamp,
        "recipients": [str(x) for x in a.recipients],
    }


def master_goal_to_dict(g: MasterGoal) -> dict[str, Any]:
    """Serialize :class:`~src.modules.metaplan_registry.MasterGoal`."""
    return {
        "id": g.id,
        "title": g.title,
        "priority": float(g.priority),
    }


def kernel_snapshot_to_json_dict(snap: KernelSnapshotV1) -> dict[str, Any]:
    """
    Full snapshot as a JSON-ready dict (matches :data:`~src.persistence.schema.SCHEMA_VERSION`).

    **Advisory-only blobs** (do not change MalAbs / Bayes / final_action; hints and telemetry):
    ``experience_digest``, ``metaplan_goals``, ``somatic_marker_weights``,
    ``skill_learning_tickets``, ``user_model_*``, ``subjective_*``, ``escalation_session_*``,
    ``uchi_soto_profiles``, and DAO draft lists — see schema descriptions and ADR 0007.
    """
    return {
        "schema_version": int(snap.schema_version),
        "episodes": list(snap.episodes),
        "internal_id_verify": f"V11:{int(snap.schema_version)}:arq.jvof",
        "narrative_counter": int(snap.narrative_counter),
        "identity_state": dict(snap.identity_state),
        "experience_digest": str(snap.experience_digest or ""),
        "forgiveness_memories": {str(k): dict(v) for k, v in snap.forgiveness_memories.items()},
        "forgiveness_cycle": int(snap.forgiveness_cycle),
        "forgiveness_recent_positives": int(snap.forgiveness_recent_positives),
        "weakness_type": str(snap.weakness_type),
        "weakness_base_intensity": snap.weakness_base_intensity
        if snap.weakness_base_intensity is None
        else float(snap.weakness_base_intensity),
        "weakness_records": list(snap.weakness_records),
        "weakness_cycle": int(snap.weakness_cycle),
        "bayesian_pruning_threshold": float(snap.bayesian_pruning_threshold),
        "bayesian_gray_zone_threshold": float(snap.bayesian_gray_zone_threshold),
        "bayesian_hypothesis_weights": [float(x) for x in snap.bayesian_hypothesis_weights],
        "locus_alpha": float(snap.locus_alpha),
        "locus_beta": float(snap.locus_beta),
        "locus_success_history": int(snap.locus_success_history),
        "locus_failure_history": int(snap.locus_failure_history),
        "variability_seed": snap.variability_seed
        if snap.variability_seed is None
        else int(snap.variability_seed),
        "variability_active": bool(snap.variability_active),
        "pruned_actions": {str(k): list(v) for k, v in snap.pruned_actions.items()},
        "dao_record_counter": int(snap.dao_record_counter),
        "dao_records": list(snap.dao_records),
        "dao_alerts": list(snap.dao_alerts),
        "constitution_l1_drafts": list(snap.constitution_l1_drafts),
        "constitution_l2_drafts": list(snap.constitution_l2_drafts),
        "dao_proposal_counter": int(snap.dao_proposal_counter),
        "dao_participants": list(snap.dao_participants),
        "dao_proposals": list(snap.dao_proposals),
        "metaplan_goals": list(snap.metaplan_goals),
        "somatic_marker_weights": {
            str(k): float(v) for k, v in snap.somatic_marker_weights.items()
        },
        "skill_learning_tickets": list(snap.skill_learning_tickets),
        "user_model_frustration_streak": int(snap.user_model_frustration_streak),
        "user_model_premise_concern_streak": int(snap.user_model_premise_concern_streak),
        "user_model_last_circle": str(snap.user_model_last_circle),
        "user_model_turns_observed": int(snap.user_model_turns_observed),
        "user_model_cognitive_pattern": str(snap.user_model_cognitive_pattern),
        "user_model_risk_band": str(snap.user_model_risk_band),
        "user_model_judicial_phase": str(snap.user_model_judicial_phase),
        "subjective_turn_index": int(snap.subjective_turn_index),
        "subjective_stimulus_ema": float(snap.subjective_stimulus_ema),
        "escalation_session_strikes": int(snap.escalation_session_strikes),
        "escalation_session_idle_turns": int(snap.escalation_session_idle_turns),
        "uchi_soto_profiles": list(snap.uchi_soto_profiles),
        "migratory_body": dict(snap.migratory_body),
    }
