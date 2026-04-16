"""
Explicit snapshot schema migrations (JSON dict in → dict at :data:`~src.persistence.schema.SCHEMA_VERSION`).

Load path: :func:`~src.persistence.json_store.snapshot_from_dict` delegates here before
constructing :class:`~src.persistence.schema.KernelSnapshotV1`. Keep steps small and test each
migration with golden fixtures under ``tests/fixtures/snapshots/``.
"""

from __future__ import annotations

from typing import Any

from .schema import SCHEMA_VERSION


def migrate_v1_to_v2(d: dict[str, Any]) -> dict[str, Any]:
    """
    Schema 1 → 2: constitution draft lists (V12.2) introduced; older files omit them.
    """
    m = dict(d)
    m["schema_version"] = 2
    m.setdefault("constitution_l1_drafts", [])
    m.setdefault("constitution_l2_drafts", [])
    return m


def apply_schema3_defaults(m: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure keys added after early snapshots exist before ``KernelSnapshotV1(**merged)``.

    Safe to call for payloads already at the current schema (idempotent for defaults).
    """
    merged = dict(m)
    merged.setdefault("dao_proposals", [])
    merged.setdefault("dao_participants", [])
    merged.setdefault("dao_proposal_counter", 0)
    if "experience_digest" not in merged:
        merged["experience_digest"] = ""
    merged.setdefault("metaplan_goals", [])
    merged.setdefault("somatic_marker_weights", {})
    merged.setdefault("skill_learning_tickets", [])
    merged.setdefault("user_model_frustration_streak", 0)
    merged.setdefault("user_model_premise_concern_streak", 0)
    merged.setdefault("user_model_last_circle", "neutral_soto")
    merged.setdefault("user_model_turns_observed", 0)
    merged.setdefault("user_model_cognitive_pattern", "none")
    merged.setdefault("user_model_risk_band", "low")
    merged.setdefault("user_model_judicial_phase", "")
    merged.setdefault("subjective_turn_index", 0)
    merged.setdefault("subjective_stimulus_ema", 0.55)
    merged.setdefault("escalation_session_strikes", 0)
    merged.setdefault("escalation_session_idle_turns", 0)
    merged.setdefault("uchi_soto_profiles", [])
    merged.setdefault("constitution_l1_drafts", [])
    merged.setdefault("constitution_l2_drafts", [])
    return merged


def migrate_v2_to_v3(d: dict[str, Any]) -> dict[str, Any]:
    """Schema 2 → 3: DAO proposal state, v7–v11 checkpoint fields, and advisory blobs."""
    m = dict(d)
    m["schema_version"] = 3
    return apply_schema3_defaults(m)


def migrate_raw_to_current(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Apply the migration chain until ``schema_version`` matches :data:`SCHEMA_VERSION`,
    then apply current-schema defaults (for partially-written v3 files).
    """
    merged = dict(raw)
    try:
        ver = int(merged.get("schema_version", 0))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid schema_version: {merged.get('schema_version')!r}") from e

    if ver == 0:
        raise ValueError("schema_version is required for snapshot migration")
    if ver > SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version {ver!r}; expected 1, 2, or {SCHEMA_VERSION}")

    while ver < SCHEMA_VERSION:
        if ver == 1:
            merged = migrate_v1_to_v2(merged)
            ver = 2
        elif ver == 2:
            merged = migrate_v2_to_v3(merged)
            ver = SCHEMA_VERSION
        else:
            raise ValueError(f"Cannot migrate from schema_version {ver!r}")

    if merged.get("schema_version") != SCHEMA_VERSION:
        merged["schema_version"] = SCHEMA_VERSION

    return apply_schema3_defaults(merged)
