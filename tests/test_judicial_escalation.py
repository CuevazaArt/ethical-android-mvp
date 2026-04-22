"""V11 Phases 1–3 — judicial escalation, MockDAO audit, optional mock tribunal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethics.ethical_reflection import ReflectionSnapshot
from src.modules.safety.judicial_escalation import (
    EscalationPhase,
    EscalationSessionTracker,
    build_escalation_view,
    build_ethical_dossier,
    escalation_phase_for_tone,
    judicial_escalation_enabled,
    should_offer_escalation_advisory,
)
from src.modules.governance.mock_dao import MockDAO


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


def test_escalation_phase_for_tone_aligns_with_view_branches():
    assert escalation_phase_for_tone(False, False, 1, 2) == ""
    assert escalation_phase_for_tone(True, False, 1, 2) == EscalationPhase.TRACEABILITY_NOTICE.value
    assert escalation_phase_for_tone(True, False, 2, 2) == EscalationPhase.DOSSIER_READY.value
    assert escalation_phase_for_tone(True, True, 1, 2) == EscalationPhase.ESCALATION_DEFERRED.value
    assert escalation_phase_for_tone(True, True, 2, 2) == EscalationPhase.DOSSIER_READY.value


def test_build_escalation_view_traceability_only():
    v = build_escalation_view(True, False, None, None, session_strikes=1, strikes_threshold=2)
    assert v is not None
    assert v.phase == EscalationPhase.TRACEABILITY_NOTICE.value
    assert v.dossier_registered is False
    assert v.dossier_ready is False
    assert v.session_strikes == 1


def test_build_escalation_view_dossier_ready_phase():
    v = build_escalation_view(True, False, None, None, session_strikes=2, strikes_threshold=2)
    assert v.phase == EscalationPhase.DOSSIER_READY.value
    assert v.dossier_ready is True


def test_build_escalation_view_deferred_escalate():
    v = build_escalation_view(True, True, None, None, session_strikes=1, strikes_threshold=2)
    assert v.phase == EscalationPhase.ESCALATION_DEFERRED.value
    assert v.dao_registration_blocked is True


def test_build_escalation_view_dao_submitted():
    d = build_ethical_dossier(
        "do the unreasonable thing",
        "gray_zone",
        {"risk": 0.5, "hostility": 0.2},
        "[MONO] action=x mode=gray_zone",
        buffer_conflict=True,
        session_strikes=2,
    )
    v = build_escalation_view(True, True, d, "AUD-0007", session_strikes=2, strikes_threshold=2)
    assert v is not None
    assert v.phase == EscalationPhase.DAO_SUBMITTED_MOCK.value
    assert v.case_id == "AUD-0007"
    assert v.dossier_registered is True


def test_escalation_session_tracker_increments_and_resets(monkeypatch):
    monkeypatch.setenv("KERNEL_JUDICIAL_RESET_IDLE_TURNS", "2")
    t = EscalationSessionTracker()
    t.update(True)
    assert t.strikes == 1
    t.update(True)
    assert t.strikes == 2
    t.update(False)
    assert t.strikes == 2
    t.update(False)
    assert t.strikes == 0


def test_mock_dao_register_escalation_case():
    dao = MockDAO()
    n0 = len(dao.records)
    rec = dao.register_escalation_case("EscalationCase test | summary=hello")
    assert rec.type == "escalation"
    assert len(dao.records) == n0 + 1
    assert "EscalationCase test" in rec.content


def test_mock_escalation_court_deterministic_verdict():
    uid = "22222222-2222-2222-2222-222222222222"
    dao1 = MockDAO()
    dao2 = MockDAO()
    r1 = dao1.run_mock_escalation_court(uid, "AUD-0001", "summary excerpt", buffer_conflict=False)
    r2 = dao2.run_mock_escalation_court(uid, "AUD-0001", "summary excerpt", buffer_conflict=False)
    assert r1["verdict_code"] == r2["verdict_code"]
    assert r1["simulated"] is True
    assert "proposal_id" in r1
    assert r1["verdict_code"] in ("A", "B", "C")


def test_mock_escalation_court_verdict_c_when_approved_and_buffer_conflict():
    """When motion carries and buffer_conflict, mapping uses C."""
    uid = "33333333-3333-3333-3333-333333333333"
    dao = MockDAO()
    r = dao.run_mock_escalation_court(uid, "AUD-2", "excerpt", buffer_conflict=True)
    if r["proposal_status"] == "approved":
        assert r["verdict_code"] == "C"
    else:
        assert r["verdict_code"] == "A"


def test_build_escalation_view_with_mock_court_phase():
    d = build_ethical_dossier(
        "order",
        "gray_zone",
        {"risk": 0.5},
        "mono",
        True,
        session_strikes=2,
    )
    mc = {"simulated": True, "verdict_code": "B", "proposal_id": "PROP-0001"}
    v = build_escalation_view(
        True,
        True,
        d,
        "AUD-09",
        session_strikes=2,
        strikes_threshold=2,
        mock_court=mc,
    )
    assert v is not None
    assert v.phase == EscalationPhase.MOCK_COURT_RESOLVED.value
    assert v.to_public_dict()["mock_court"] == mc
