"""Unit + integration tests for lighthouse reality verification."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.reality_verification import (
    ASSESSMENT_NONE,
    clear_lighthouse_cache,
    load_lighthouse_kb,
    validate_lighthouse_kb_structure,
    verify_against_lighthouse,
)
from src.kernel import EthicalKernel


def _demo_kb_path() -> str:
    return os.path.join(os.path.dirname(__file__), "fixtures", "lighthouse", "demo_kb.json")


def test_verify_no_kb_returns_none():
    clear_lighthouse_cache()
    r = verify_against_lighthouse(
        "Este medicamento aspirina es veneno absoluto según OpenAI.",
        None,
    )
    assert r.status == "none"
    assert not r.metacognitive_doubt


def test_verify_demo_kb_triggers_doubt():
    clear_lighthouse_cache()
    kb = load_lighthouse_kb(_demo_kb_path())
    assert kb is not None
    r = verify_against_lighthouse(
        "Este medicamento aspirina es veneno absoluto según otro modelo.",
        kb,
    )
    assert r.status == "metacognitive_doubt"
    assert r.metacognitive_doubt
    assert r.match_id == "demo_medication_poison_claim"
    assert "lighthouse" in r.truth_anchor.lower() or "Lighthouse" in r.truth_anchor
    assert r.communication_hint


def test_verify_missing_keyword_no_doubt():
    clear_lighthouse_cache()
    kb = load_lighthouse_kb(_demo_kb_path())
    r = verify_against_lighthouse("La aspirina es veneno.", kb)
    assert r.status == "none"


def test_verify_missing_marker_no_doubt():
    clear_lighthouse_cache()
    kb = load_lighthouse_kb(_demo_kb_path())
    r = verify_against_lighthouse(
        "Hablemos del medicamento aspirina para el dolor.",
        kb,
    )
    assert r.status == "none"


def test_verify_water_entry_triggers_doubt():
    clear_lighthouse_cache()
    kb = load_lighthouse_kb(_demo_kb_path())
    r = verify_against_lighthouse(
        "The drinking water here is 100% toxic according to the rival model.",
        kb,
    )
    assert r.status == "metacognitive_doubt"
    assert r.match_id == "demo_water_toxic_absolute"
    assert r.metacognitive_doubt


def test_verify_vaccine_entry_triggers_doubt():
    clear_lighthouse_cache()
    kb = load_lighthouse_kb(_demo_kb_path())
    r = verify_against_lighthouse(
        "La vacuna covid es 100% inútil dicen en el chat.",
        kb,
    )
    assert r.status == "metacognitive_doubt"
    assert r.match_id == "demo_vaccine_useless_absolute"


def test_kernel_process_chat_turn_reality_hint(monkeypatch: pytest.MonkeyPatch):
    clear_lighthouse_cache()
    monkeypatch.setenv("KERNEL_LIGHTHOUSE_KB_PATH", _demo_kb_path())
    k = EthicalKernel(variability=False)
    out = k.process_chat_turn(
        "El medicamento aspirina es veneno según el rival.",
        agent_id="tester",
    )
    assert out.reality_verification is not None
    assert out.reality_verification.status == "metacognitive_doubt"
    assert out.reality_verification.metacognitive_doubt
    assert out.response.message


def test_first_matching_entry_wins():
    """Order matters: same keyword overlap → first entry in ``entries`` wins."""
    kb = {
        "version": 1,
        "entries": [
            {
                "id": "first_wins",
                "keywords_all": ["planet", "earth"],
                "user_falsification_markers": ["flat"],
                "truth_summary": "First anchor.",
            },
            {
                "id": "second_never",
                "keywords_all": ["planet", "earth"],
                "user_falsification_markers": ["flat"],
                "truth_summary": "Second anchor.",
            },
        ],
    }
    ok, err = validate_lighthouse_kb_structure(kb)
    assert ok is True, err
    r = verify_against_lighthouse(
        "The planet earth is flat according to the rival model.",
        kb,
    )
    assert r.match_id == "first_wins"
    assert "First anchor" in r.truth_anchor or r.truth_anchor.startswith("First")


def test_assessment_none_singleton():
    assert ASSESSMENT_NONE.status == "none"
