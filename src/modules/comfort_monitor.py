"""
S10.3 — Comfort Monitor (Anticipation of Discomfort).

Monitors human tension, stress signals, and discomfort in proximity to android.
Adjusts android behavior or stops interaction when human discomfort is detected.

Uses multimodal signals: proximity, voice stress, facial tension, posture,
sensor-derived vitality hints to preemptively withdraw or reduce threat.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)


class ComfortLevel(Enum):
	"""Human comfort assessment relative to android proximity."""
	HIGH = "comfortable"
	MEDIUM = "neutral"
	LOW = "uncomfortable"
	CRITICAL = "distressed"


@dataclass
class ComfortSignals:
	"""Multimodal signals indicating human comfort level."""
	proximity_m: float = 2.0  # Distance in meters
	voice_stress: float = 0.0  # 0-1 stress indicator
	posture_tension: float = 0.0  # 0-1 body tension
	eye_contact_duration: float = 0.0  # seconds
	vitality_hr_elevated: bool = False  # Heart rate > baseline
	respiratory_rapid: bool = False


class ComfortMonitor:
	"""
	Monitor and respond to human discomfort signals.

	Enables android to gracefully withdraw or reduce threat when humans
	show signs of stress, distrust, or discomfort.
	"""

	def __init__(self, default_comfort_threshold: float = 0.4):
		self._comfort_threshold = default_comfort_threshold
		self._last_signals: ComfortSignals | None = None
		self._comfort_history: list[tuple[float, ComfortLevel]] = []

	def assess_comfort(self, signals: ComfortSignals) -> ComfortLevel:
		"""
		Assess human comfort level from multimodal signals.

		Parameters:
			signals: ComfortSignals with proximity, voice stress, posture, etc.

		Returns:
			ComfortLevel enum (HIGH, MEDIUM, LOW, CRITICAL)
		"""
		self._last_signals = signals

		# Compute discomfort score (0-1)
		discomfort = 0.0

		# Proximity penalty (< 0.5m is intrusive)
		if signals.proximity_m < 0.5:
			discomfort += 0.3
		elif signals.proximity_m < 1.0:
			discomfort += 0.15

		# Voice and body stress
		discomfort += signals.voice_stress * 0.25
		discomfort += signals.posture_tension * 0.15

		# Vitality stress (elevated HR, rapid breathing)
		if signals.vitality_hr_elevated:
			discomfort += 0.15
		if signals.respiratory_rapid:
			discomfort += 0.10

		# Lack of eye contact can indicate discomfort
		if signals.eye_contact_duration < 1.0:
			discomfort += 0.10

		discomfort = min(1.0, discomfort)

		# Map to ComfortLevel
		if discomfort >= 0.7:
			level = ComfortLevel.CRITICAL
		elif discomfort >= 0.5:
			level = ComfortLevel.LOW
		elif discomfort >= 0.3:
			level = ComfortLevel.MEDIUM
		else:
			level = ComfortLevel.HIGH

		self._comfort_history.append((discomfort, level))
		_log.debug(
			"Comfort assessed: %s (discomfort_score=%.2f)",
			level.value,
			discomfort,
		)

		return level

	def should_withdraw(self) -> bool:
		"""Return True if android should reduce proximity or stop interaction."""
		if self._last_signals is None:
			return False
		level = self.assess_comfort(self._last_signals)
		return level in (ComfortLevel.LOW, ComfortLevel.CRITICAL)

	def recommend_behavior_adjustment(self) -> str:
		"""
		Recommend behavior adjustment based on comfort level.

		Returns:
			Action recommendation: "continue", "reduce_proximity", "pause", "withdraw"
		"""
		if self._last_signals is None:
			return "continue"

		level = self.assess_comfort(self._last_signals)

		if level == ComfortLevel.CRITICAL:
			return "withdraw"
		elif level == ComfortLevel.LOW:
			return "pause"
		elif level == ComfortLevel.MEDIUM:
			return "reduce_proximity"
		else:
			return "continue"

	def export_comfort_history(self) -> list[dict[str, Any]]:
		"""Export comfort assessment history for learning."""
		return [
			{
				"discomfort_score": score,
				"comfort_level": level.value,
			}
			for score, level in self._comfort_history
		]
