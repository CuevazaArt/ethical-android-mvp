"""JSON Schema validation, explicit snapshot serde, and migration round-trip checks."""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.persistence import SCHEMA_VERSION, extract_snapshot
from src.persistence.json_store import snapshot_from_dict
from src.persistence.migrations import migrate_raw_to_current
from src.persistence.schema import KernelSnapshotV1
from src.persistence.snapshot_serde import kernel_snapshot_to_json_dict
from src.persistence.snapshot_validate import (
    validate_migrated_snapshot_dict,
    validate_snapshot_for_apply,
)

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "snapshots"


def test_extracted_snapshot_serializes_and_validates():
    k = EthicalKernel(variability=False)
    snap = extract_snapshot(k)
    d = kernel_snapshot_to_json_dict(snap)
    assert d["schema_version"] == SCHEMA_VERSION
    validate_migrated_snapshot_dict(d)


def test_apply_snapshot_rejects_malformed_dao_record():
    k = EthicalKernel(variability=False)
    snap = extract_snapshot(k)
    snap.dao_records = [{"not": "a valid audit line"}]
    with pytest.raises(ValueError, match="JSON Schema"):
        validate_snapshot_for_apply(snap)


def test_migration_v1_chain_produces_valid_full_dict():
    raw = json.loads((_FIXTURES / "minimal_v1.json").read_text(encoding="utf-8"))
    merged = migrate_raw_to_current(raw)
    snap = KernelSnapshotV1(**merged)
    d = kernel_snapshot_to_json_dict(snap)
    validate_migrated_snapshot_dict(d)


def test_snapshot_from_dict_validates_after_construct():
    snap = snapshot_from_dict({"schema_version": 1})
    validate_snapshot_for_apply(snap)
