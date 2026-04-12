"""
Hub audit — single calibration-line format for DAO transparency (nomadic, hub events).

Keeps a stable prefix so logs can be filtered without parsing free-form strings everywhere.
"""

from __future__ import annotations

import json
from typing import Any


def register_hub_calibration(dao: Any, kind: str, payload: dict[str, Any]) -> None:
    """Append one MockDAO calibration row: ``HubAudit:<kind>:<json>``."""
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)[:1900]
    dao.register_audit("calibration", f"HubAudit:{kind}:{body}")


def record_dao_integrity_alert(
    dao: Any,
    *,
    summary: str,
    scope: str = "local_audit",
    principled_transparency: bool = True,
) -> None:
    """
    Loud, auditable signal — local ledger only (mock DAO).

    Aligns with docs/proposals/PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md: no covert “guerrilla”;
    transparency as infrastructure. Does not broadcast to a real network.
    """
    register_hub_calibration(
        dao,
        "dao_integrity",
        {
            "summary": (summary or "")[:800],
            "scope": (scope or "local_audit")[:120],
            "principled_transparency": principled_transparency,
        },
    )
