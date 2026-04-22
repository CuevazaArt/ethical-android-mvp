"""Phase 4 nomadic handshake: canonical commitment + Ed25519 verification."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.kernel import EthicalKernel
from src.modules.governance.existential_serialization import (
    HANDSHAKE_ALGORITHM_V1,
    canonical_narrative_commitment_hex,
    export_nomadic_handshake_bundle,
    narrative_integrity_phase4,
    verify_nomadic_handshake,
)


def test_canonical_commitment_stable_for_same_kernel():
    k = EthicalKernel(variability=False, llm_mode="local")
    a = canonical_narrative_commitment_hex(k)
    b = canonical_narrative_commitment_hex(k)
    assert len(a) == 64
    assert a == b


def test_handshake_export_and_verify_roundtrip():
    priv = Ed25519PrivateKey.generate()
    k = EthicalKernel(variability=False, llm_mode="local")
    bundle = export_nomadic_handshake_bundle(k, "continuity test", private_key=priv)
    assert bundle.get("ok") is True
    assert bundle.get("algorithm") == HANDSHAKE_ALGORITHM_V1
    assert bundle.get("commitment_sha256")
    vr = verify_nomadic_handshake(k, bundle, public_key=priv.public_key())
    assert vr.get("ok") is True
    assert vr.get("commitment_matches") is True
    assert vr.get("signature_valid") is True


def test_handshake_fails_after_state_mutation():
    priv = Ed25519PrivateKey.generate()
    k = EthicalKernel(variability=False, llm_mode="local")
    bundle = export_nomadic_handshake_bundle(k, "x", private_key=priv)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[1]()
    k.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)
    vr = verify_nomadic_handshake(k, bundle, public_key=priv.public_key())
    assert vr.get("ok") is False
    assert vr.get("commitment_matches") is False


def test_narrative_integrity_phase4_embeds_handshake():
    priv = Ed25519PrivateKey.generate()
    k = EthicalKernel(variability=False, llm_mode="local")
    bundle = export_nomadic_handshake_bundle(k, "y", private_key=priv)
    report = narrative_integrity_phase4(k, bundle)
    assert report.get("handshake_ok") is True
    assert report.get("commitment_sha256") == bundle.get("commitment_sha256")


def test_verify_rejects_truncated_bundle():
    k = EthicalKernel(variability=False, llm_mode="local")
    vr = verify_nomadic_handshake(k, {})
    assert vr.get("ok") is False
    assert "missing" in (vr.get("error") or "").lower()
