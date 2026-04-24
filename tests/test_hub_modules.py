"""NomadIdentity, ReparationVault, MLEthicsTuner stubs."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.ethics.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from src.modules.governance.hub_audit import record_dao_integrity_alert, register_hub_calibration
from src.modules.governance.mock_dao import MockDAO
from src.modules.governance.nomad_identity import nomad_identity_public
from src.modules.memory.reparation_vault import (
    STATE_INTENT,
    STATE_POST_TRIBUNAL,
    ReparationVault,
    clear_reparation_vault_cases_for_tests,
    maybe_register_reparation_after_mock_court,
)


def test_hub_audit_calibration_prefix():
    dao = MockDAO()
    n0 = len(dao.records)
    register_hub_calibration(dao, "test_kind", {"a": 1})
    assert len(dao.records) == n0 + 1
    assert "HubAudit:test_kind" in dao.records[-1].content


def test_hub_audit_dao_integrity_alert():
    dao = MockDAO()
    n0 = len(dao.records)
    record_dao_integrity_alert(dao, summary="Simulated corrupt directive X", scope="lab")
    assert len(dao.records) == n0 + 1
    assert "HubAudit:dao_integrity" in dao.records[-1].content
    assert "principled_transparency" in dao.records[-1].content


def test_nomad_identity_public_shape():
    k = EthicalKernel(variability=False)
    d = nomad_identity_public(k)
    assert d["label"] == "NomadIdentity"
    assert "immortality_layer_snapshots" in d


def test_reparation_vault_off_by_default():
    dao = MockDAO()
    vault = ReparationVault(dao)
    assert vault.reparation_vault_mock_enabled() is False


def test_reparation_vault_registers_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    clear_reparation_vault_cases_for_tests()
    k = EthicalKernel(variability=False)
    vault = ReparationVault(k.dao)
    n0 = len(k.dao.records)
    vault.register_reparation_intent("third party harmed", case_ref="CASE-1")
    assert len(k.dao.records) == n0 + 1
    assert "ReparationVaultV1" in k.dao.records[-1].content
    st = vault.get_reparation_case("CASE-1")
    assert st is not None
    assert st["state"] == STATE_INTENT


def test_maybe_register_after_mock_court(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    clear_reparation_vault_cases_for_tests()
    dao = MockDAO()
    n0 = len(dao.records)
    maybe_register_reparation_after_mock_court(
        dao,
        {
            "verdict_code": "B",
            "verdict_label": "android_refusal_ratified",
            "proposal_id": "PROP-0001",
        },
        "case-uuid-1234",
    )
    assert len(dao.records) == n0 + 1
    assert "mock tribunal" in dao.records[-1].content.lower()
    assert "ReparationVaultV1" in dao.records[-1].content
    vault = ReparationVault(dao)
    st = vault.get_reparation_case("case-uuid-1234")
    assert st["state"] == STATE_POST_TRIBUNAL


def test_maybe_register_skips_when_no_court(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    dao = MockDAO()
    n0 = len(dao.records)
    maybe_register_reparation_after_mock_court(dao, None, "x")
    assert len(dao.records) == n0


def test_ml_ethics_tuner_logs_on_gray_zone(monkeypatch):
    monkeypatch.setenv("KERNEL_ML_ETHICS_TUNER_LOG", "1")
    import json
    from types import SimpleNamespace

    from src.modules.ethics.ethical_poles import Verdict

    k = EthicalKernel(variability=False)
    n0 = len(k.dao.records)
    moral = SimpleNamespace(global_verdict=Verdict.GRAY_ZONE)
    dec = SimpleNamespace(decision_mode="gray_zone", moral=moral, final_action="act_x")
    r = SimpleNamespace(decision=dec)
    maybe_log_gray_zone_tuning_opportunity(k.dao, r, kernel=k)
    assert len(k.dao.records) > n0
    raw = k.dao.records[-1].content
    assert "MLEthicsTuner:" in raw
    payload = json.loads(raw.split("MLEthicsTuner:", 1)[1].strip())
    assert payload["schema"] == "MLEthicsTunerEventV1"
    assert payload["decision_mode"] == "gray_zone"
    assert "content_sha256_short" in payload
