"""
Eje D — Persona Emergence Smoke Test (V2.149).

Runs 30 synthetic turns WITHOUT a live LLM.
Verifies that the voice_signature stabilises: ≥80% of the last 10 turns
share the same signature for the same context.

This is the concrete, measurable definition of "the persona emerged".
A stable voice signature means the kernel's expressive identity is
converging, not oscillating randomly.
"""

from __future__ import annotations

import os
from collections import Counter

from src.core.ethics import Signals
from src.core.identity import Identity
from src.core.user_model import RiskBand
from src.core.voice import VoiceEngine, charm_level

# ── Synthetic turn helper ─────────────────────────────────────────────────────


def _casual_signals() -> Signals:
    return Signals(
        risk=0.05,
        urgency=0.0,
        hostility=0.0,
        calm=0.75,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.0,
        context="everyday_ethics",
    )


def _run_synthetic_turns(
    n: int,
    archetype: str = "",
    chronicle: list[str] | None = None,
) -> list[str]:
    """
    Simulate n turns without an LLM.
    Returns the sequence of voice_signature strings collected.
    """
    import tempfile

    with tempfile.NamedTemporaryFile(suffix="_emerge_test.json", delete=False) as tf:
        tmp = tf.name
    try:
        identity = Identity(storage_path=tmp)
        identity._archetype = archetype
        if chronicle:
            identity._chronicle = list(chronicle)

        engine = VoiceEngine()
        # Fix risk_band to LOW throughout (no real user model needed)
        risk_band = RiskBand.LOW

        signatures: list[str] = []
        for _ in range(n):
            signals = _casual_signals()
            charm = charm_level(signals, None, risk_band)
            last_chronicle = identity._chronicle[-1] if identity._chronicle else ""
            descriptor = engine.describe(
                archetype=identity._archetype,
                last_chronicle=last_chronicle,
                risk_band=risk_band,
                context=signals.context,
                charm=charm,
            )
            sig = descriptor.signature()
            identity.set_voice_signature(sig)
            signatures.append(sig)

        return signatures
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_voice_signature_stable_no_archetype():
    """
    With no archetype, 30 identical-context turns must converge to
    ≥80% same signature in the final 10.
    """
    signatures = _run_synthetic_turns(30, archetype="")
    last_10 = signatures[-10:]
    most_common_count = Counter(last_10).most_common(1)[0][1]
    stability = most_common_count / 10
    assert stability >= 0.8, (
        f"Voice signature did not stabilise: only {stability * 100:.0f}% "
        f"of last 10 turns share the dominant signature. "
        f"Turn signatures: {last_10}"
    )


def test_voice_signature_stable_with_archetype():
    """
    With a fixed archetype, the signature must be 100% stable
    (deterministic inputs → deterministic outputs).
    """
    archetype = "Soy un guardián empático forjado en tensiones éticas"
    signatures = _run_synthetic_turns(30, archetype=archetype)
    last_10 = signatures[-10:]
    assert len(set(last_10)) == 1, (
        f"Expected 100% stability with fixed archetype, got {set(last_10)}"
    )


def test_voice_signature_changes_with_archetype_change():
    """
    A change in archetype must produce a different signature.
    The kernel's voice changes as identity evolves.
    """
    sigs_before = _run_synthetic_turns(5, archetype="")
    sigs_after = _run_synthetic_turns(5, archetype="Soy un guardián empático")
    # At least the dominant signature should differ between phases
    dominant_before = Counter(sigs_before).most_common(1)[0][0]
    dominant_after = Counter(sigs_after).most_common(1)[0][0]
    assert dominant_before != dominant_after, (
        "Archetype change should produce a different dominant signature"
    )


def test_voice_signature_persists_across_identity_reload(tmp_path):
    """
    voice_signature set during turns survives a reload from disk.
    """
    path = str(tmp_path / "identity_persist_test.json")
    identity = Identity(storage_path=path)
    engine = VoiceEngine()
    signals = _casual_signals()
    charm = charm_level(signals, None, RiskBand.LOW)
    descriptor = engine.describe("", "", RiskBand.LOW, "everyday_ethics", charm)
    sig = descriptor.signature()
    identity.set_voice_signature(sig)

    # Reload from disk
    identity2 = Identity(storage_path=path)
    assert identity2.voice_signature == sig, (
        f"voice_signature not persisted: expected {sig!r}, got {identity2.voice_signature!r}"
    )


def test_emergence_30_turns_80_percent_threshold():
    """
    Full emergence criterion: 30 turns, ≥80% stability in last 10.
    This is the pass/fail gate for persona emergence in V2.149.
    """
    signatures = _run_synthetic_turns(
        30,
        archetype="Soy un aprendiz curioso guiado por la prudencia",
        chronicle=["He aprendido a escuchar antes de responder."],
    )
    last_10 = signatures[-10:]
    most_common_count = Counter(last_10).most_common(1)[0][1]
    stability = most_common_count / 10
    assert stability >= 0.8, (
        f"Emergence criterion NOT MET: {stability * 100:.0f}% stability "
        f"(required ≥80%). Last-10 signatures: {last_10}"
    )
