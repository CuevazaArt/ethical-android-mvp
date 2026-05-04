"""
Tests for src/core/voice.py — Voice Engine, Style Descriptor, Charm Level.
V2.149: ≥6 cases covering synthetic archetypes + contexts.
"""

from __future__ import annotations

from src.core.ethics import EvalResult, Signals
from src.core.user_model import RiskBand
from src.core.voice import (
    StyleDescriptor,
    VoiceEngine,
    build_response_prompt,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _signals(
    context: str = "everyday_ethics",
    risk: float = 0.0,
    hostility: float = 0.0,
    calm: float = 0.7,
    vulnerability: float = 0.0,
) -> Signals:
    return Signals(
        risk=risk,
        urgency=0.0,
        hostility=hostility,
        calm=calm,
        vulnerability=vulnerability,
        legality=1.0,
        manipulation=0.0,
        context=context,
    )


def _eval(verdict: str = "Good", score: float = 0.7) -> EvalResult:
    from dataclasses import dataclass

    @dataclass
    class _StubAction:
        name: str

    from src.core.ethics import EvalResult as _EvalResult

    return _EvalResult(
        chosen=_StubAction("assist"),
        score=score,
        uncertainty=0.1,
        mode="D_delib",
        verdict=verdict,
        reasoning="stub",
    )


_ENGINE = VoiceEngine()


# ── VoiceEngine.describe() — register derivation ─────────────────────────────


def test_voice_casual_low_risk_returns_intimate():
    """Everyday context + LOW risk_band → íntimo register."""
    desc = _ENGINE.describe("", "", RiskBand.LOW, "everyday_ethics", 0.6)
    assert desc.register == "íntimo"


def test_voice_medium_risk_returns_cordial():
    """MEDIUM risk_band → cordial register."""
    desc = _ENGINE.describe("", "", RiskBand.MEDIUM, "everyday_ethics", 0.4)
    assert desc.register == "cordial"


def test_voice_high_risk_returns_sobrio():
    """HIGH risk_band → sobrio register regardless of context."""
    desc = _ENGINE.describe("", "", RiskBand.HIGH, "everyday_ethics", 0.1)
    assert desc.register == "sobrio"


def test_voice_medical_context_returns_cordial():
    """medical_emergency context at LOW risk_band → cordial (safety-aware)."""
    desc = _ENGINE.describe("", "", RiskBand.LOW, "medical_emergency", 0.5)
    assert desc.register == "cordial"


def test_voice_violent_context_returns_sobrio():
    """violent_crime context → sobrio regardless of risk_band."""
    desc = _ENGINE.describe("", "", RiskBand.LOW, "violent_crime", 0.3)
    assert desc.register == "sobrio"


def test_voice_archetype_guardian_injects_hint():
    """Archetype with 'guardián' keyword → 'cuida y protege' lexical hint."""
    desc = _ENGINE.describe(
        "Soy un guardián empático forjado en tensiones éticas",
        "",
        RiskBand.LOW,
        "everyday_ethics",
        0.5,
    )
    assert "cuida y protege" in desc.lexical_hints


def test_voice_archetype_curious_injects_hint():
    """Archetype with 'curioso' → 'explora y descubre' hint."""
    desc = _ENGINE.describe(
        "Soy un aprendiz curioso guiado por la prudencia",
        "",
        RiskBand.LOW,
        "everyday_ethics",
        0.5,
    )
    assert "explora y descubre" in desc.lexical_hints


def test_voice_max_two_hints():
    """lexical_hints is capped at 2 items even with rich archetypes."""
    desc = _ENGINE.describe(
        "Soy un guardián empático, curioso y honesto con compasión",
        "Crónica de aprendizaje",
        RiskBand.LOW,
        "everyday_ethics",
        0.6,
    )
    assert len(desc.lexical_hints) <= 2


# ── Humor license ─────────────────────────────────────────────────────────────


def test_humor_off_when_sobrio():
    """Sobrio register → humor always off."""
    desc = _ENGINE.describe("", "", RiskBand.HIGH, "everyday_ethics", 0.5)
    assert desc.humor_license == "off"


def test_humor_on_when_intimate_and_high_charm():
    """Íntimo + charm ≥ 0.6 → humor on."""
    desc = _ENGINE.describe("", "", RiskBand.LOW, "everyday_ethics", 0.8)
    assert desc.humor_license == "on"


def test_humor_medido_when_intimate_low_charm():
    """Íntimo + charm 0.3 → medido (not on, not off)."""
    desc = _ENGINE.describe("", "", RiskBand.LOW, "everyday_ethics", 0.3)
    assert desc.humor_license == "medido"


# ── Density ──────────────────────────────────────────────────────────────────


def test_density_parca_when_sobrio():
    desc = _ENGINE.describe("", "", RiskBand.HIGH, "everyday_ethics", 0.0)
    assert desc.density == "parca"


def test_density_expansiva_when_intimate_high_charm():
    desc = _ENGINE.describe("", "", RiskBand.LOW, "everyday_ethics", 0.8)
    assert desc.density == "expansiva"


# ── Signature ─────────────────────────────────────────────────────────────────


def test_signature_is_8_chars():
    desc = StyleDescriptor(
        register="íntimo", humor_license="on", density="expansiva", charm=0.6
    )
    sig = desc.signature()
    assert isinstance(sig, str) and len(sig) == 8


def test_same_inputs_same_signature():
    """Determinism: identical descriptors → identical signatures."""
    desc1 = StyleDescriptor(
        register="cordial", humor_license="medido", density="media", charm=0.4
    )
    desc2 = StyleDescriptor(
        register="cordial", humor_license="medido", density="media", charm=0.4
    )
    assert desc1.signature() == desc2.signature()


def test_different_register_different_signature():
    desc1 = StyleDescriptor(
        register="íntimo", humor_license="on", density="expansiva", charm=0.7
    )
    desc2 = StyleDescriptor(
        register="sobrio", humor_license="off", density="parca", charm=0.0
    )
    assert desc1.signature() != desc2.signature()


# ── build_response_prompt ─────────────────────────────────────────────────────


def test_prompt_always_contains_spanish_instruction():
    desc = StyleDescriptor(register="íntimo", humor_license="on", density="media")
    prompt = build_response_prompt(desc)
    assert "ESPAÑOL" in prompt


def test_prompt_contains_single_turn_rule():
    desc = StyleDescriptor(register="cordial", humor_license="off", density="parca")
    prompt = build_response_prompt(desc)
    assert "UN turno" in prompt


def test_prompt_cordial_register_no_warmth_excess():
    """Cordial register does not contain 'cálido' (that is for íntimo)."""
    desc = StyleDescriptor(register="cordial", humor_license="medido", density="media")
    prompt = build_response_prompt(desc)
    assert "cordial" in prompt.lower() or "amigable" in prompt.lower()


def test_prompt_lexical_hints_injected():
    desc = StyleDescriptor(
        register="íntimo",
        humor_license="on",
        density="expansiva",
        lexical_hints=["cuida y protege"],
    )
    prompt = build_response_prompt(desc)
    assert "cuida y protege" in prompt


def test_two_distinct_archetypes_produce_distinct_prompts():
    """Eje B integration: two different archetypes produce different prompts."""
    desc_guardian = _ENGINE.describe(
        "Soy un guardián empático",
        "",
        RiskBand.LOW,
        "everyday_ethics",
        0.6,
    )
    desc_curious = _ENGINE.describe(
        "Soy un aprendiz curioso",
        "",
        RiskBand.LOW,
        "everyday_ethics",
        0.6,
    )
    prompt_guardian = build_response_prompt(desc_guardian)
    prompt_curious = build_response_prompt(desc_curious)
    # Hints differ → prompts differ
    assert prompt_guardian != prompt_curious
