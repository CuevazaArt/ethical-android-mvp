"""
Hub audit — single calibration-line format for DAO transparency (nomadic, hub events).

Keeps a stable prefix so logs can be filtered without parsing free-form strings everywhere.
"""

from __future__ import annotations

import json
from typing import Any, Dict


def register_hub_calibration(dao: Any, kind: str, payload: Dict[str, Any]) -> None:
    """Append one MockDAO calibration row: ``HubAudit:<kind>:<json>``."""
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)[:1900]
    dao.register_audit("calibration", f"HubAudit:{kind}:{body}")
