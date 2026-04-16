"""
Safety Interlock & Hardware E-Stop Module — **DEMO / SCAFFOLDING**.

Implements the physical and logic circuit breaker for the autonomous agent.
Priority: 0 (Absolute override).

.. warning::

   The reset token is read from ``KERNEL_ESTOP_RESET_TOKEN`` (env var) with a
   **hard-coded fallback** ``TRUSTED_RESET_V1``.  A production system would
   require:

   * A cryptographic challenge-response reset protocol.
   * Hardware binding (HSM / TPM nonce, physical key switch).
   * Audit logging of every reset attempt (success or failure).

   Until then, treat this module as a **structural placeholder** for *where*
   an E-stop fits in the kernel safety chain.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from enum import Enum

_log = logging.getLogger(__name__)

_DEFAULT_RESET_TOKEN = "TRUSTED_RESET_V1"


class EStopSource(Enum):
    PHYSICAL_BUTTON = "physical_button"
    CRITICAL_SENSOR = "critical_sensor"
    KERNEL_VETO = "kernel_veto"
    REMOTE_KILL = "remote_kill"


@dataclass
class EStopStatus:
    active: bool
    source: EStopSource | None
    timestamp: float
    reason: str


class SafetyInterlock:
    """
    **Demo** Hardware and Logic Interlock.

    Managed by the OLA (Orquestador Local de Autonomía).  See module docstring
    for production hardening requirements.
    """

    def __init__(self) -> None:
        self._estop_active = False
        self._source: EStopSource | None = None
        self._reason = ""
        self._last_trigger = 0.0
        self._reset_token = os.environ.get("KERNEL_ESTOP_RESET_TOKEN", _DEFAULT_RESET_TOKEN)

    def trigger_estop(self, source: EStopSource, reason: str) -> None:
        """Activate the Emergency Stop (cannot be overridden until manual reset)."""
        self._estop_active = True
        self._source = source
        self._reason = reason
        self._last_trigger = time.time()
        _log.critical(
            "!!! EMERGENCY STOP TRIGGERED !!! Source: %s, Reason: %s",
            source.value,
            reason,
        )

    def reset_estop(self, secure_token: str) -> bool:
        """Reset the E-stop if *secure_token* matches the configured token."""
        if secure_token == self._reset_token:
            self._estop_active = False
            self._source = None
            self._reason = ""
            _log.warning("Emergency Stop manually reset.")
            return True
        _log.warning("E-stop reset rejected — invalid token.")
        return False

    @property
    def status(self) -> EStopStatus:
        return EStopStatus(
            active=self._estop_active,
            source=self._source,
            timestamp=self._last_trigger,
            reason=self._reason,
        )

    def is_safe_to_operate(self) -> bool:
        """Kernel check: can we even move?"""
        return not self._estop_active
