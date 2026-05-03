#!/usr/bin/env python3
"""
DEPRECATED — swarm_sync.py (V2.159 sanitation).

This script is a compatibility shim. The "swarm" vocabulary was retired
in V2.159.  Use ``scripts/fleet_sync.py`` instead.

Usage:
    python scripts/fleet_sync.py --cycle <cycle> --msg "<message>"
"""

import sys
import warnings

warnings.warn(
    "scripts/swarm_sync.py is deprecated (retired in V2.159). "
    "Use scripts/fleet_sync.py instead.",
    DeprecationWarning,
    stacklevel=1,
)

print(
    "[DEPRECATED] swarm_sync.py was retired in V2.159. "
    "Please use fleet_sync.py instead:\n"
    "  python scripts/fleet_sync.py --cycle <cycle> --msg '<message>'"
)
sys.exit(1)
