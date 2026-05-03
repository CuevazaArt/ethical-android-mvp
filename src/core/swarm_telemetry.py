# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
DEPRECATED — swarm_telemetry (V2.159 sanitation).

The "swarm" vocabulary was retired in V2.159.  This module is a shim that
re-exports the renamed symbols from ``src.core.fleet_telemetry`` while
emitting a :class:`DeprecationWarning` on import.

Migration:
    Replace ``from src.core.swarm_telemetry import ScoutReport, SwarmLedger``
    with     ``from src.core.fleet_telemetry import InstanceReport, FleetLedger``

This shim will be removed in a future release.
"""

import warnings as _warnings

_warnings.warn(
    "src.core.swarm_telemetry is deprecated (retired in V2.159). "
    "Use src.core.fleet_telemetry instead: "
    "InstanceReport replaces ScoutReport, FleetLedger replaces SwarmLedger.",
    DeprecationWarning,
    stacklevel=2,
)

from src.core.fleet_telemetry import FLEET_LOG_DIR as SWARM_LOG_DIR  # noqa: E402
from src.core.fleet_telemetry import FleetLedger as SwarmLedger  # noqa: E402
from src.core.fleet_telemetry import InstanceReport as ScoutReport  # noqa: E402

__all__ = ["ScoutReport", "SwarmLedger", "SWARM_LOG_DIR"]
