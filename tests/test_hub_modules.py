"""NomadIdentity, ReparationVault, MLEthicsTuner stubs."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.hub_audit import record_dao_integrity_alert, register_hub_calibration
from src.modules.mock_dao import MockDAO
from src.modules.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from src.modules.nomad_identity import nomad_identity_public
from src.modules.reparation_vault import (
    maybe_register_reparation_after_mock_court,
    register_reparation_intent,
    reparation_vault_mock_enabled,
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
    assert reparation_vault_mock_enabled() is False


def test_reparation_vault_registers_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    k = EthicalKernel(variability=False)
    n0 = len(k.dao.records)
    register_reparation_intent(k.dao, "third party harmed", case_ref="CASE-1")
    assert len(k.dao.records) == n0 + 1
    assert "ReparationVault" in k.dao.records[-1].content


def test_maybe_register_after_mock_court(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    dao = MockDAO()
    n0 = len(dao.records)
    maybe_register_reparation_after_mock_court(
        dao,
        {"verdict_code": "B", "verdict_label": "android_refusal_ratified", "proposal_id": "PROP-0001"},
        "case-uuid-1234",
    )
    assert len(dao.records) == n0 + 1
    assert "mock tribunal" in dao.records[-1].content.lower()


def test_maybe_register_skips_when_no_court(monkeypatch):
    monkeypatch.setenv("KERNEL_REPARATION_VAULT_MOCK", "1")
    dao = MockDAO()
    n0 = len(dao.records)
    maybe_register_reparation_after_mock_court(dao, None, "x")
    assert len(dao.records) == n0


def test_ml_ethics_tuner_logs_on_gray_zone(monkeypatch):
    monkeypatch.setenv("KERNEL_ML_ETHICS_TUNER_LOG", "1")
    from types import SimpleNamespace

    from src.modules.ethical_poles import Verdict

    k = EthicalKernel(variability=False)
    n0 = len(k.dao.records)
    moral = SimpleNamespace(global_verdict=Verdict.GRAY_ZONE)
    dec = SimpleNamespace(decision_mode="gray_zone", moral=moral)
    r = SimpleNamespace(decision=dec)
    maybe_log_gray_zone_tuning_opportunity(k.dao, r)
    assert len(k.dao.records) > n0
    assert "MLEthicsTuner" in k.dao.records[-1].content
