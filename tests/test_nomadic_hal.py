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


def test_migration_audit_no_gps_by_default():
    k = EthicalKernel(variability=False)
    p = migration_audit_payload(k, destination_hardware_id="phone-abc")
    assert p["destination_hardware_id"] == "phone-abc"
    assert "gps" not in str(p).lower()
    assert "location" not in p
