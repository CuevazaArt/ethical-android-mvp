"""
Safety Interlock & Hardware E-Stop Module.

Implements the physical and logic circuit breaker for the autonomous agent.
Priority: 0 (Absolute override).
"""

import time
from dataclasses import dataclass
from enum import Enum


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
    Hardware and Logic Interlock.
    Managed by the OLA (Orquestador Local de Autonomía).
    """

    def __init__(self):
        self._estop_active = False
        self._source = None
        self._reason = ""
        self._last_trigger = 0.0

    def trigger_estop(self, source: EStopSource, reason: str):
        """
        Activates the Emergency Stop. This cannot be overridden by software/DAO
        until a manual reset (or secure protocol) is performed.
        """
        self._estop_active = True
        self._source = source
        self._reason = reason
        self._last_trigger = time.time()
        print(f"[SAFETY] !!! EMERGENCY STOP TRIGGERED !!! Source: {source.value}, Reason: {reason}")

    def reset_estop(self, secure_token: str):
        """
        Resets the E-Stop. Requires specific credentials or tokens.
        """
        if secure_token == "TRUSTED_RESET_V1":
            self._estop_active = False
            self._source = None
            self._reason = ""
            print("[SAFETY] Emergency Stop manually reset.")
            return True
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
