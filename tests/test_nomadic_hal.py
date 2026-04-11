"""HAL + existential serialization stubs (nomadic instantiation design)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.existential_serialization import (
    TransmutationPhase,
    build_continuity_token_stub,
    migration_audit_payload,
    narrative_integrity_self_check_stub,
    nomad_migration_audit_enabled,
    record_nomadic_migration_audit,
    simulate_nomadic_migration,
)
from src.modules.hardware_abstraction import (
    ComputeTier,
    apply_hardware_context,
    default_mobile_context,
    default_server_context,
    sensor_delta_narrative,
)


def test_hardware_context_defaults():
    s = default_server_context()
    m = default_mobile_context()
    assert s.compute_tier == ComputeTier.SERVER_HIGH
    assert "camera" in m.available_sensors
    line = sensor_delta_narrative(s, m)
    assert "Compute tier" in line


def test_apply_hal_on_kernel():
    k = EthicalKernel(variability=False)
    apply_hardware_context(k, default_mobile_context())
    assert k._hal_context.compute_tier == ComputeTier.EDGE_MOBILE


def test_continuity_token_stub():
    k = EthicalKernel(variability=False)
    t = build_continuity_token_stub(k, "thinking about dignity")
    assert t.phase == TransmutationPhase.ENCAPSULATE
    assert "dignity" in t.thought_summary
    assert len(t.identity_fingerprint) == 16


def test_narrative_integrity_stub():
    k = EthicalKernel(variability=False)
    r = narrative_integrity_self_check_stub(k)
    assert r["ok"] is True
    assert "chain_sha256" in r
    assert len(r["chain_sha256"]) == 64


def test_migration_audit_no_gps_by_default():
    k = EthicalKernel(variability=False)
    p = migration_audit_payload(k, destination_hardware_id="phone-abc")
    assert p["destination_hardware_id"] == "phone-abc"
    assert "gps" not in str(p).lower()
    assert "location" not in p


def test_migration_audit_thought_line_in_continuity():
    k = EthicalKernel(variability=False)
    p = migration_audit_payload(k, thought_line="considering compassion")
    assert "compassion" in p["continuity"]["thought_summary"]


def test_simulate_nomadic_migration_applies_hal(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_MIGRATION_AUDIT", "0")
    k = EthicalKernel(variability=False)
    r = simulate_nomadic_migration(k, k.dao, profile="mobile", destination_hardware_id="p1")
    assert r["hardware_context"]["compute_tier"] == "edge_mobile"
    assert r["dao_audit_recorded"] is False


def test_record_nomadic_migration_audit_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_MIGRATION_AUDIT", "1")
    assert nomad_migration_audit_enabled() is True
    k = EthicalKernel(variability=False)
    n0 = len(k.dao.records)
    ok = record_nomadic_migration_audit(k.dao, k, destination_hardware_id="dev-1", thought_line="x")
    assert ok is True
    assert len(k.dao.records) > n0
    assert "HubAudit:nomadic_migration" in k.dao.records[-1].content
