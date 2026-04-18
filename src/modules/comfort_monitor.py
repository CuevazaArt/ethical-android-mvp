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

	# Proximity thresholds (meters) — extracted from magic numbers
	_PROXIMITY_INTRUSIVE_M = 0.5
	_PROXIMITY_CLOSE_M = 1.0

	# Discomfort score weights
	_PROXIMITY_INTRUSIVE_PENALTY = 0.3
	_PROXIMITY_CLOSE_PENALTY = 0.15
	_VOICE_STRESS_WEIGHT = 0.25
	_POSTURE_TENSION_WEIGHT = 0.15
	_HR_ELEVATED_WEIGHT = 0.15
	_RESPIRATORY_RAPID_WEIGHT = 0.10
	_EYE_CONTACT_WEIGHT = 0.10
	_MIN_EYE_CONTACT_S = 1.0

	# ComfortLevel thresholds (discomfort score 0-1)
	_THRESHOLD_CRITICAL = 0.7
	_THRESHOLD_LOW = 0.5
	_THRESHOLD_MEDIUM = 0.3

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

		# Proximity penalty
		if signals.proximity_m < self._PROXIMITY_INTRUSIVE_M:
			discomfort += self._PROXIMITY_INTRUSIVE_PENALTY
		elif signals.proximity_m < self._PROXIMITY_CLOSE_M:
			discomfort += self._PROXIMITY_CLOSE_PENALTY

		# Voice and body stress
		discomfort += signals.voice_stress * self._VOICE_STRESS_WEIGHT
		discomfort += signals.posture_tension * self._POSTURE_TENSION_WEIGHT

		# Vitality stress (elevated HR, rapid breathing)
		if signals.vitality_hr_elevated:
			discomfort += self._HR_ELEVATED_WEIGHT
		if signals.respiratory_rapid:
			discomfort += self._RESPIRATORY_RAPID_WEIGHT

		# Lack of eye contact can indicate discomfort
		if signals.eye_contact_duration < self._MIN_EYE_CONTACT_S:
			discomfort += self._EYE_CONTACT_WEIGHT

		discomfort = min(1.0, discomfort)

		# Map to ComfortLevel
		if discomfort >= self._THRESHOLD_CRITICAL:
			level = ComfortLevel.CRITICAL
		elif discomfort >= self._THRESHOLD_LOW:
			level = ComfortLevel.LOW
		elif discomfort >= self._THRESHOLD_MEDIUM:
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
