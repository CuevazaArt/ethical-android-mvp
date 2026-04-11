"""Extract / apply :class:`KernelSnapshotV1` without changing ethical algorithms."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, cast

import numpy as np

from src.modules.forgiveness import WeightedMemory
from src.modules.metaplan_registry import MasterGoal
from src.modules.skill_learning_registry import SkillLearningTicket, Status
from src.modules.mock_dao import AuditRecord, SolidarityAlert
from src.modules.narrative import BodyState, NarrativeEpisode
from src.modules.narrative_identity import NarrativeIdentityState
from src.modules.variability import VariabilityConfig, VariabilityEngine
from src.modules.subjective_time import SubjectiveClock
from src.modules.weakness_pole import WeaknessRecord, WeaknessType

from .schema import SCHEMA_VERSION, KernelSnapshotV1

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def episode_to_dict(ep: NarrativeEpisode) -> Dict[str, Any]:
    d = asdict(ep)
    d["body_state"] = asdict(ep.body_state)
    if d.get("affect_pad") is not None:
        d["affect_pad"] = list(d["affect_pad"])
    return d


def episode_from_dict(d: Dict[str, Any]) -> NarrativeEpisode:
    body = BodyState(**d["body_state"])
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
        ethical_score=float(d["ethical_score"]),
        decision_mode=d["decision_mode"],
        sigma=float(d["sigma"]),
        context=d["context"],
        affect_pad=pad,
        affect_weights=dict(d["affect_weights"]) if d.get("affect_weights") is not None else None,
    )


def extract_snapshot(kernel: "EthicalKernel") -> KernelSnapshotV1:
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
        identity_state=asdict(mem.identity.state),
        experience_digest=getattr(mem, "experience_digest", "") or "",
        forgiveness_memories={k: asdict(v) for k, v in fg.memories.items()},
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
        dao_records=[asdict(r) for r in dao.records],
        dao_alerts=[asdict(a) for a in dao.alerts],
        constitution_l1_drafts=list(getattr(kernel, "constitution_l1_drafts", []) or []),
        constitution_l2_drafts=list(getattr(kernel, "constitution_l2_drafts", []) or []),
        dao_proposal_counter=dao_st["proposal_counter"],
        dao_participants=dao_st["participants"],
        dao_proposals=dao_st["proposals"],
        metaplan_goals=[asdict(g) for g in kernel.metaplan.goals()],
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
        subjective_turn_index=int(kernel.subjective_clock.turn_index),
        subjective_stimulus_ema=float(kernel.subjective_clock.stimulus_ema),
        escalation_session_strikes=int(kernel.escalation_session.strikes),
        escalation_session_idle_turns=int(kernel.escalation_session.idle_turns),
    )


def apply_snapshot(kernel: "EthicalKernel", snap: KernelSnapshotV1) -> None:
    """Restore mutable state. Caller must ensure ``snap`` matches :data:`SCHEMA_VERSION`."""
    if snap.schema_version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version {snap.schema_version}; expected {SCHEMA_VERSION}")

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
            intensity=float(r["intensity"]),
            timestamp=float(r["timestamp"]),
        )
        for r in snap.weakness_records
    ]
    w._cycle = snap.weakness_cycle

    kernel.bayesian.pruning_threshold = snap.bayesian_pruning_threshold
    kernel.bayesian.gray_zone_threshold = snap.bayesian_gray_zone_threshold
    kernel.bayesian.hypothesis_weights = np.array(snap.bayesian_hypothesis_weights, dtype=float)

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

    mp: List[MasterGoal] = []
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

    tickets: List[SkillLearningTicket] = []
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
