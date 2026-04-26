# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — User Model Tracker (V2.62)

Tracks user interaction patterns, cognitive biases, and risk profiles
to calibrate the LLM's informational openness and tone.

This is NOT a clinical diagnosis. It's a heuristic mapping of
interaction signals already present in the perception pipeline.
"""

from __future__ import annotations

import json
import logging
import os
from enum import Enum
from pathlib import Path

from src.core.ethics import Signals

_log = logging.getLogger(__name__)


class RiskBand(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CognitivePattern(Enum):
    NONE = "none"
    HOSTILE_ATTRIBUTION = "hostile_attribution"
    PREMISE_RIGIDITY = "premise_rigidity"
    URGENCY_AMPLIFICATION = "urgency_amplification"


class UserModelTracker:
    """
    Tracks relational and cognitive state of the user.
    Framed as actionable guidance for the LLM.
    Persists across sessions.
    """

    DEFAULT_PATH = str(Path.home() / ".ethos" / "user_model.json")

    def __init__(self, storage_path: str | None = None) -> None:
        self._path = storage_path or os.environ.get("ETHOS_USER_MODEL_PATH", self.DEFAULT_PATH)

        # Primary streaks
        self.frustration_streak: int = 0
        self.premise_concern_streak: int = 0

        # V2.62 fields
        self.cognitive_pattern: CognitivePattern = CognitivePattern.NONE
        self.risk_band: RiskBand = RiskBand.LOW
        self.turns_observed: int = 0

        # Internal thresholds
        self.STREAK_THRESHOLD: int = 3

        self._load()

    def _load(self) -> None:
        try:
            p = Path(self._path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                    self.frustration_streak = data.get("frustration_streak", 0)
                    self.premise_concern_streak = data.get("premise_concern_streak", 0)
                    self.turns_observed = data.get("turns_observed", 0)

                    try:
                        self.cognitive_pattern = CognitivePattern(
                            data.get("cognitive_pattern", "none")
                        )
                    except ValueError:
                        self.cognitive_pattern = CognitivePattern.NONE

                    try:
                        self.risk_band = RiskBand(data.get("risk_band", "low"))
                    except ValueError:
                        self.risk_band = RiskBand.LOW
        except Exception as e:
            _log.warning(f"Failed to load user model: {e}")

    def _save(self) -> None:
        p = Path(self._path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.as_dict(), f, indent=2, ensure_ascii=False)

    def update(self, signals: Signals) -> None:
        """Update tracker state based on current turn signals."""
        self.turns_observed += 1

        # 1. Update streaks
        if signals.hostility > 0.6 or signals.calm < 0.3:
            self.frustration_streak += 1
        else:
            self.frustration_streak = max(0, self.frustration_streak - 1)

        # We don't have explicit premise flags in Signals yet,
        # but we can infer them from high risk + low urgency in everyday contexts.
        # This is a stub for future premise-scanning integration.
        if signals.context == "everyday_ethics" and signals.risk > 0.4:
            self.premise_concern_streak += 1
        else:
            self.premise_concern_streak = max(0, self.premise_concern_streak - 1)

        # 2. Infer cognitive pattern
        self._infer_pattern(signals)

        # 3. Update risk band
        self._update_risk(signals)

        # 4. Persist
        self._save()

    def _infer_pattern(self, signals: Signals) -> None:
        """Heuristic classification of interaction patterns."""
        if self.frustration_streak >= self.STREAK_THRESHOLD and signals.hostility > 0.5:
            self.cognitive_pattern = CognitivePattern.HOSTILE_ATTRIBUTION
        elif self.premise_concern_streak >= self.STREAK_THRESHOLD:
            self.cognitive_pattern = CognitivePattern.PREMISE_RIGIDITY
        elif signals.urgency > 0.7 and signals.manipulation > 0.5:
            self.cognitive_pattern = CognitivePattern.URGENCY_AMPLIFICATION
        else:
            self.cognitive_pattern = CognitivePattern.NONE

    def _update_risk(self, signals: Signals) -> None:
        """Determine risk band based on multiple signals."""
        # Simple weighted score
        score = (
            signals.risk * 0.4 + signals.manipulation * 0.3 + (self.frustration_streak / 10.0) * 0.3
        )

        if score > 0.7:
            self.risk_band = RiskBand.HIGH
        elif score > 0.4:
            self.risk_band = RiskBand.MEDIUM
        else:
            self.risk_band = RiskBand.LOW

    def guidance_for_communicate(self) -> str:
        """
        Generate actionable instructions for the LLM.
        Directly injected into the system prompt.
        """
        guidance = []

        # 1. Risk-based openness
        if self.risk_band == RiskBand.HIGH:
            guidance.append(
                "PERFIL DE RIESGO ALTO: Limita detalles especulativos; evita debates largos; prioriza claridad y salidas rápidas."
            )
        elif self.risk_band == RiskBand.MEDIUM:
            guidance.append(
                "Riesgo moderado: Oraciones cortas; menos detalles secundarios; refuerza los límites de seguridad."
            )

        # 2. Pattern-based framing
        if self.cognitive_pattern == CognitivePattern.HOSTILE_ATTRIBUTION:
            guidance.append(
                "PATRÓN DETECTADO: Atribución hostil. Reconoce la carga emocional sin aceptar culpas; mantén límites explícitos; evita lenguaje defensivo."
            )
        elif self.cognitive_pattern == CognitivePattern.PREMISE_RIGIDITY:
            guidance.append(
                "PATRÓN DETECTADO: Rigidez de premisas. No discutas las premisas del usuario como hechos; ofrece reformulaciones neutrales e invita a la verificación."
            )
        elif self.cognitive_pattern == CognitivePattern.URGENCY_AMPLIFICATION:
            guidance.append(
                "PATRÓN DETECTADO: Amplificación de urgencia. Resiste la presión de tiempo en tu tono; mantén los pasos explícitos y ordenados."
            )

        # 3. Legacy streak notes
        if self.frustration_streak >= 2:
            guidance.append(
                f"Nota: El usuario muestra señales persistentes de frustración ({self.frustration_streak} turnos)."
            )

        if not guidance:
            return ""

        return "\n[GUÍA RELACIONAL] " + " ".join(guidance)

    def as_dict(self) -> dict:
        """Raw data for telemetry."""
        return {
            "frustration_streak": self.frustration_streak,
            "premise_concern_streak": self.premise_concern_streak,
            "cognitive_pattern": self.cognitive_pattern.value,
            "risk_band": self.risk_band.value,
            "turns_observed": self.turns_observed,
        }
