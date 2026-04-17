"""Lighthouse KB structure validation and fixture regression (epistemic tooling)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.reality_verification import (
    clear_lighthouse_cache,
    validate_lighthouse_kb_file,
    validate_lighthouse_kb_structure,
)


def _demo_kb_path() -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", "lighthouse", "demo_kb.json")


def test_demo_kb_file_validates():
    clear_lighthouse_cache()
    ok, errors = validate_lighthouse_kb_file(_demo_kb_path())
    assert ok is True, errors
    assert errors == []


def test_validate_rejects_non_object_root():
    ok, errors = validate_lighthouse_kb_structure(None)  # type: ignore[arg-type]
    assert ok is False
    assert any("None" in e or "object" in e for e in errors)


def test_validate_rejects_missing_entries_array():
    ok, errors = validate_lighthouse_kb_structure({"version": 1})
    assert ok is False
    assert any("entries" in e.lower() for e in errors)


def test_validate_rejects_bad_entry_fields():
    kb = {
        "version": 1,
        "entries": [
            {
                "id": "",
                "keywords_all": [],
                "user_falsification_markers": [],
                "truth_summary": "x",
            }
        ],
    }
    ok, errors = validate_lighthouse_kb_structure(kb)
    assert ok is False
    assert len(errors) >= 3


def test_validate_accepts_minimal_valid_entry():
    kb = {
        "version": 1,
        "entries": [
            {
                "id": "smoke_entry",
                "keywords_all": ["alpha", "beta"],
                "user_falsification_markers": ["false claim"],
                "truth_summary": "Anchor text.",
            }
        ],
    }
    ok, errors = validate_lighthouse_kb_structure(kb)
    assert ok is True, errors
