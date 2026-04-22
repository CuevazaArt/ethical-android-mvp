"""Conduct guide validation (vertical Phase 3)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.context_distillation import (
    load_and_validate_conduct_guide_from_env,
    validate_conduct_guide_dict,
)
from src.persistence.schema import SCHEMA_VERSION


def test_validate_conduct_guide_ok():
    data = {
        "version": 1,
        "ethical_non_negotiables": ["a"],
        "checkpoint_compatible_schema": SCHEMA_VERSION,
    }
    ok, err = validate_conduct_guide_dict(data)
    assert ok is True
    assert err == []


def test_validate_conduct_guide_bad_version():
    ok, err = validate_conduct_guide_dict({"version": 2})
    assert ok is False
    assert "version_must_equal_1" in err


def test_validate_conduct_guide_schema_mismatch():
    ok, err = validate_conduct_guide_dict({"version": 1, "checkpoint_compatible_schema": 0})
    assert ok is False
    assert any("checkpoint_compatible_schema_mismatch" in e for e in err)


def test_load_and_validate_from_env(tmp_path, monkeypatch):
    p = tmp_path / "guide.json"
    p.write_text(
        '{"version": 1, "ethical_non_negotiables": [], "checkpoint_compatible_schema": '
        + str(SCHEMA_VERSION)
        + "}",
        encoding="utf-8",
    )
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_PATH", str(p))
    data, errs = load_and_validate_conduct_guide_from_env()
    assert data is not None
    assert errs == []
