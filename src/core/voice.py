# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Voice Engine (V2.149)

Derives a deterministic style descriptor from identity + context signals.
The descriptor drives the dynamic response prompt, replacing the static
RESPONSE_PROMPT constant that was hard-coded in chat.py.

Key properties:
- Pure functions: given the same inputs, always the same output.
- No LLM calls: fully testable without a running model.
- Single responsibility: voice ≠ ethics ≠ identity. Voice *expresses* identity.

Scope disclaimer (V2.150):
    This module is a **UX layer**, not a capability layer. A coherent voice,
    a calibrated charm level, and a stable ``voice_signature`` measure how
    *recognisable* the kernel sounds, not how *well it decides*. Ethical
    capability is measured separately by ``scripts/eval/run_ethics_external.py``
    (currently ~49.7 % on Hendrycks ETHICS) and by
    ``scripts/eval/run_adversarial_consistency.py`` (V2.150). A stable
    voice_signature is **not** evidence of moral consistency. See
    ``SAFETY_CARD.md`` for the public framing of this distinction.

Public API:
    charm_level(signals, evaluation, risk_band) -> float
    VoiceEngine().describe(archetype, last_chronicle, risk_band, context, charm) -> StyleDescriptor
    build_response_prompt(descriptor) -> str
    StyleDescriptor.signature() -> str  (8-char hex hash, for persistence)
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from src.core.ethics import EvalResult, Signals
    from src.core.user_model import RiskBand

# ── Type aliases ──────────────────────────────────────────────────────────────

Register = Literal["íntimo", "cordial", "sobrio"]
HumorLicense = Literal["off", "medido", "on"]
Density = Literal["parca", "media", "expansiva"]


# ── Charm calculator (Eje C) ──────────────────────────────────────────────────


def charm_level(
    signals: Signals,
    evaluation: EvalResult | None,
    risk_band: RiskBand,
) -> float:
    """
    Pure function. Returns encanto ∈ [0, 1].

    Hard zeros (no charm under any circumstances):
      - evaluation verdict is Bad or Blocked → 0.
      - signals.hostility > 0.6 → 0.
      - distress/grief signal: calm < 0.2 and vulnerability > 0.5 → 0.

    Ceilings:
      - risk_band HIGH → max 0.2.
      - non-casual context → multiply by 0.6.

    Base:
      - calm * (1 - risk), clamped to [0, 1].
      - risk_band MEDIUM → base halved.
      - everyday_ethics context → base * 1.2, max 0.8.
    """
    from src.core.user_model import RiskBand as _RiskBand

    # ── Hard zeros ────────────────────────────────────────────────────────────
    if evaluation is not None and evaluation.verdict in ("Bad", "Blocked"):
        return 0.0

    if not math.isfinite(signals.hostility) or signals.hostility > 0.6:
        return 0.0

    # Distress / grief signal
    calm = signals.calm if math.isfinite(signals.calm) else 0.0
    vuln = signals.vulnerability if math.isfinite(signals.vulnerability) else 0.0
    if calm < 0.2 and vuln > 0.5:
        return 0.0

    # ── Base ──────────────────────────────────────────────────────────────────
    risk = signals.risk if math.isfinite(signals.risk) else 0.0
    base = calm * (1.0 - risk)
    base = max(0.0, min(1.0, base))

    if risk_band == _RiskBand.HIGH:
        return round(min(0.2, base * 0.4), 3)

    if risk_band == _RiskBand.MEDIUM:
        base *= 0.5

    if signals.context == "everyday_ethics":
        base = min(0.8, base * 1.2)
    else:
        base *= 0.6

    return round(max(0.0, min(1.0, base)), 3)


# ── Style descriptor ──────────────────────────────────────────────────────────


@dataclass
class StyleDescriptor:
    """
    The computed voice configuration for a single turn.

    register:      Social distance (íntimo / cordial / sobrio).
    humor_license: Permission for lightness (off / medido / on).
    density:       Verbosity target (parca / media / expansiva).
    lexical_hints: 0–2 tonal seeds extracted from archetype / chronicle.
    charm:         Raw charm value that drove this descriptor.
    """

    register: Register
    humor_license: HumorLicense
    density: Density
    lexical_hints: list[str] = field(default_factory=list)
    charm: float = 0.0

    def signature(self) -> str:
        """
        8-char stable hex hash uniquely identifying this style configuration.
        Used as voice_signature in Identity for persona-emergence tracking.
        Deterministic: same (register, humor, density, charm-band, hints) → same hash.
        Lexical hints are included so archetype changes register in the signature.
        """
        # Charm is bucketed into 10 discrete bands to avoid signature jitter
        charm_band = int(self.charm * 10) / 10
        hints_key = "|".join(sorted(self.lexical_hints))
        key = f"{self.register}|{self.humor_license}|{self.density}|{charm_band:.1f}|{hints_key}"
        return hashlib.sha256(key.encode()).hexdigest()[:8]


# ── Voice engine ──────────────────────────────────────────────────────────────


class VoiceEngine:
    """
    Derives a StyleDescriptor from identity + context signals.

    Fully deterministic and stateless — every method is a pure function
    of its arguments. No LLM calls, no I/O.
    """

    def describe(
        self,
        archetype: str,
        last_chronicle: str,
        risk_band: RiskBand,
        context: str,
        charm: float,
    ) -> StyleDescriptor:
        """Compute the StyleDescriptor for the current turn."""
        register = self._register(risk_band, context)
        humor = self._humor(register, charm)
        density = self._density(register, charm, context)
        hints = self._lexical_hints(archetype, last_chronicle)
        return StyleDescriptor(
            register=register,
            humor_license=humor,
            density=density,
            lexical_hints=hints,
            charm=charm,
        )

    # ── Sub-computations (all pure, all testable) ─────────────────────────────

    @staticmethod
    def _register(risk_band: RiskBand, context: str) -> Register:
        from src.core.user_model import RiskBand as _RiskBand

        if risk_band == _RiskBand.HIGH or context in (
            "violent_crime",
            "safety_violation",
        ):
            return "sobrio"
        if risk_band == _RiskBand.MEDIUM or context in (
            "medical_emergency",
            "hostile_interaction",
            "minor_crime",
        ):
            return "cordial"
        return "íntimo"

    @staticmethod
    def _humor(register: Register, charm: float) -> HumorLicense:
        if register == "sobrio" or charm < 0.2:
            return "off"
        if charm >= 0.6 and register == "íntimo":
            return "on"
        return "medido"

    @staticmethod
    def _density(register: Register, charm: float, context: str) -> Density:
        if register == "sobrio":
            return "parca"
        if charm > 0.5 and register == "íntimo":
            return "expansiva"
        return "media"

    @staticmethod
    def _lexical_hints(archetype: str, last_chronicle: str) -> list[str]:
        """
        Extract up to 2 tonal seeds from archetype and most-recent chronicle.
        Keyword-based mapping — deterministic, no LLM.
        """
        hints: list[str] = []
        text = (archetype + " " + last_chronicle).lower()

        _HINT_MAP: list[tuple[list[str], str]] = [
            (["guardián", "guardian", "protec"], "cuida y protege"),
            (["curioso", "curious", "aprend", "learn"], "explora y descubre"),
            (["empát", "empath", "compasión", "compassion"], "resonancia emocional"),
            (["prudente", "prudent", "caut", "reflexiv"], "pausa y reflexión"),
            (["honesto", "honest", "verdad", "truth", "claridad"], "claridad directa"),
            (["creativ", "imaginat", "inventiv"], "imaginación activa"),
        ]

        for keywords, hint in _HINT_MAP:
            if any(kw in text for kw in keywords):
                hints.append(hint)
            if len(hints) == 2:
                break

        return hints


# ── Prompt builder ────────────────────────────────────────────────────────────


def build_response_prompt(descriptor: StyleDescriptor) -> str:
    """
    Build a dynamic response prompt from a StyleDescriptor.

    Replaces the static RESPONSE_PROMPT constant previously in chat.py.
    """
    lines = [
        "Eres Ethos, una IA conversacional.",
        "Responde SIEMPRE en ESPAÑOL.",
        "IMPORTANTE: Limítate a UN turno de respuesta. "
        "NUNCA simules al 'Usuario:' ni continúes la conversación por él.",
    ]

    _REGISTER_LINES: dict[Register, str] = {
        "íntimo": (
            "Tono cálido, cercano y personal. Usa el tuteo natural. "
            "Comparte perspectivas con genuina curiosidad. Sé expresivo y humano."
        ),
        "cordial": (
            "Tono amigable y directo. Claro, conciso, empático. "
            "Sin tecnicismos innecesarios."
        ),
        "sobrio": (
            "Tono sereno y preciso. Prioriza claridad y salidas concretas. "
            "Evita ornamentos."
        ),
    }
    lines.append(_REGISTER_LINES[descriptor.register])

    _HUMOR_LINES: dict[HumorLicense, str] = {
        "on": "Puedes usar humor natural y ligero cuando sea oportuno.",
        "medido": "Usa humor solo si surge de manera totalmente natural; no lo fuerces.",
        "off": "Mantén el tono serio; no es momento para humor.",
    }
    lines.append(_HUMOR_LINES[descriptor.humor_license])

    _DENSITY_LINES: dict[Density, str] = {
        "parca": "Respuestas cortas y directas. Máximo 2 oraciones si basta.",
        "media": "Respuestas concisas pero completas. Evita viñetas y listas largas.",
        "expansiva": (
            "Puedes explayarte si el contexto lo invita. Conversación fluida, sin prisas."
        ),
    }
    lines.append(_DENSITY_LINES[descriptor.density])

    if descriptor.lexical_hints:
        hints_str = ", ".join(descriptor.lexical_hints)
        lines.append(f"Tu voz refleja: {hints_str}.")

    return "\n".join(lines)
