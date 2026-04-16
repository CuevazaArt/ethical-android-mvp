"""Explicit snapshot migration steps and golden fixtures (schema 1 → 2 → 3)."""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.persistence import (
    SCHEMA_VERSION,
    migrate_raw_to_current,
    migrate_v1_to_v2,
    migrate_v2_to_v3,
)
from src.persistence.json_store import snapshot_from_dict
from src.persistence.migrations import apply_schema3_defaults

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "snapshots"


def test_migrate_v1_to_v2_adds_draft_slots():
    out = migrate_v1_to_v2({"schema_version": 1})
    assert out["schema_version"] == 2
    assert out["constitution_l1_drafts"] == []
    assert out["constitution_l2_drafts"] == []


def test_migrate_v2_to_v3_sets_version_and_defaults():
    out = migrate_v2_to_v3({"schema_version": 2})
    assert out["schema_version"] == 3
    assert out["dao_proposals"] == []
    assert out["user_model_cognitive_pattern"] == "none"


def test_migrate_raw_to_current_chain_v1():
    merged = migrate_raw_to_current({"schema_version": 1})
    assert merged["schema_version"] == SCHEMA_VERSION
    assert merged["constitution_l1_drafts"] == []


def test_golden_minimal_v1_fixture_loads():
    raw = json.loads((_FIXTURES / "minimal_v1.json").read_text(encoding="utf-8"))
    snap = snapshot_from_dict(raw)
    assert snap.schema_version == SCHEMA_VERSION
    assert snap.dao_proposals == []


def test_golden_minimal_v2_fixture_preserves_drafts():
    raw = json.loads((_FIXTURES / "minimal_v2.json").read_text(encoding="utf-8"))
    snap = snapshot_from_dict(raw)
    assert snap.schema_version == SCHEMA_VERSION
    assert len(snap.constitution_l1_drafts) == 1
    assert snap.constitution_l1_drafts[0].get("id") == "golden_v2_draft"


def test_migrate_raw_rejects_future_version():
    with pytest.raises(ValueError, match="Unsupported schema_version"):
        migrate_raw_to_current({"schema_version": SCHEMA_VERSION + 1})


def test_apply_schema3_defaults_idempotent():
    d = {"schema_version": 3, "episodes": [], "narrative_counter": 0}
    a = apply_schema3_defaults(d)
    b = apply_schema3_defaults(a)
    assert a["schema_version"] == b["schema_version"] == 3
    assert a["dao_proposals"] == b["dao_proposals"] == []
