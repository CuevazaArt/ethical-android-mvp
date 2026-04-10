"""V11 Phase 1 — judicial escalation advisory and MockDAO audit hook."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.judicial_escalation import (
    EscalationPhase,
    build_escalation_view,
    build_ethical_dossier,
    judicial_escalation_enabled,
    should_offer_escalation_advisory,
)
from src.modules.mock_dao import MockDAO
from src.modules.ethical_reflection import ReflectionSnapshot


def test_judicial_escalation_disabled_by_default():
    assert judicial_escalation_enabled() is False


def test_judicial_escalation_enabled_via_env(monkeypatch):
    monkeypatch.setenv("KERNEL_JUDICIAL_ESCALATION", "1")
    assert judicial_escalation_enabled() is True


def test_should_offer_gray_zone_and_strain():
    ref = ReflectionSnapshot(
        pole_spread=0.5,
        pole_scores=(0.5, 0.3, 0.4),
        conflict_level="high",
        strain_index=0.5,
        will_mode="gray_zone",
        uncertainty=0.2,
        note="",
    )
    assert should_offer_escalation_advisory("gray_zone", ref, "none") is True


def test_should_not_offer_non_gray():
    ref = ReflectionSnapshot(
        pole_spread=0.1,
        pole_scores=(0.5, 0.5, 0.5),
        conflict_level="low",
        strain_index=0.1,
        will_mode="fast",
        uncertainty=0.1,
        note="",
    )
    assert should_offer_escalation_advisory("fast", ref, "none") is False


def test_build_escalation_view_traceability_only():
    v = build_escalation_view(True, False, None, None)
    assert v is not None
    assert v.phase == EscalationPhase.TRACEABILITY_NOTICE.value
    assert v.dossier_registered is False


def test_build_escalation_view_dao_submitted():
    d = build_ethical_dossier(
        "do the unreasonable thing",
        "gray_zone",
        {"risk": 0.5, "hostility": 0.2},
        "[MONO] action=x mode=gray_zone",
        buffer_conflict=True,
    )
    v = build_escalation_view(True, True, d, "AUD-0007")
    assert v is not None
    assert v.phase == EscalationPhase.DAO_SUBMITTED_MOCK.value
    assert v.case_id == "AUD-0007"
    assert v.dossier_registered is True


def test_mock_dao_register_escalation_case():
    dao = MockDAO()
    n0 = len(dao.records)
    rec = dao.register_escalation_case("EscalationCase test | summary=hello")
    assert rec.type == "escalation"
    assert len(dao.records) == n0 + 1
    assert "EscalationCase test" in rec.content
