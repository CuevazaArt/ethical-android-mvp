"""
S10.4 — Help Request Protocols.

Enables android to clearly signal when it requires human intervention.

Provides multiple channels: visual (LED patterns, gestures), acoustic (speech),
and digital (API flags) to request help in a way that reduces human uncertainty
and enables rapid, safe intervention.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)


class HelpLevel(Enum):
	"""Urgency and type of help needed."""
	INFO = "informational"  # Clarification needed
	ADVISORY = "advisory"  # Guidance recommended
	URGENT = "urgent"  # Intervention required soon
	CRITICAL = "critical"  # Immediate intervention required


class ChannelType(Enum):
	"""Communication channels for help requests."""
	VISUAL = "visual"  # LED, gestures, projection
	ACOUSTIC = "acoustic"  # Voice, speech synthesis
	DIGITAL = "digital"  # API, network signal


@dataclass
class HelpRequest:
	"""Structured help request with multiple signal channels."""
	level: HelpLevel
	reason: str
	timestamp_mono: float = 0.0
	signal_channels: list[ChannelType] | None = None


class HelpRequestProtocol:
	"""
	Protocol for android to request human help.

	Broadcasts help requests across multiple sensory channels to ensure
	humans notice and understand the android needs support.
	"""

	def __init__(self):
		self._active_help_request: HelpRequest | None = None
		self._help_history: list[HelpRequest] = []
		self._custom_handlers: dict[ChannelType, callable] = {}

	def register_channel_handler(
		self,
		channel: ChannelType,
		handler: callable,
	) -> None:
		"""Register a custom handler for a communication channel."""
		self._custom_handlers[channel] = handler
		_log.info("Registered help channel handler: %s", channel.value)

	def request_help(
		self,
		level: HelpLevel,
		reason: str,
		channels: list[ChannelType] | None = None,
	) -> HelpRequest:
		"""
		Request human help via specified channels.

		Parameters:
			level: Urgency level (info, advisory, urgent, critical)
			reason: Human-readable reason for help request
			channels: List of channels to use (visual, acoustic, digital)

		Returns:
			HelpRequest object ready for transmission
		"""
		if channels is None:
			# Default: all channels for critical, subset for others
			if level == HelpLevel.CRITICAL:
				channels = [ChannelType.VISUAL, ChannelType.ACOUSTIC, ChannelType.DIGITAL]
			elif level == HelpLevel.URGENT:
				channels = [ChannelType.ACOUSTIC, ChannelType.DIGITAL]
			else:
				channels = [ChannelType.DIGITAL]

		request = HelpRequest(
			level=level,
			reason=reason,
			signal_channels=channels,
		)

		self._active_help_request = request
		self._help_history.append(request)

		# Activate channels
		for channel in channels:
			self._activate_channel(channel, request)

		_log.warning(
			"Help request: level=%s reason=%s channels=%s",
			level.value,
			reason,
			[ch.value for ch in channels],
		)

		return request

	def _activate_channel(self, channel: ChannelType, request: HelpRequest) -> None:
		"""Activate a communication channel for help request."""
		if channel in self._custom_handlers:
			try:
				self._custom_handlers[channel](request)
			except Exception as e:
				_log.error("Error in help channel %s: %s", channel.value, e)
		else:
			# Default behavior
			if channel == ChannelType.VISUAL:
				_log.info("VISUAL: Display urgent help signal (LED pattern)")
			elif channel == ChannelType.ACOUSTIC:
				_log.info("ACOUSTIC: Speak help request: %s", request.reason)
			elif channel == ChannelType.DIGITAL:
				_log.info("DIGITAL: Transmit help request to external system")

	def clear_help_request(self) -> None:
		"""Clear active help request when help is provided or issue resolved."""
		self._active_help_request = None
		_log.info("Help request cleared")

	def get_active_request(self) -> HelpRequest | None:
		"""Return current active help request, if any."""
		return self._active_help_request

	def export_help_history(self) -> list[dict[str, Any]]:
		"""Export help request history for audit."""
		return [
			{
				"level": req.level.value,
				"reason": req.reason,
				"channels": [ch.value for ch in (req.signal_channels or [])],
			}
			for req in self._help_history
		]
