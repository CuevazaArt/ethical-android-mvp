"""
ReparationVault (MVP mock) — intended DAO treasury for third-party indemnification.

Registers **intent** lines on the audit ledger only; no balances or transfers.
After V11 **mock escalation tribunal** (``run_mock_escalation_court``), optionally
records a reparation review line when ``KERNEL_REPARATION_VAULT_MOCK`` is on.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .mock_dao import MockDAO


def reparation_vault_mock_enabled() -> bool:
    v = os.environ.get("KERNEL_REPARATION_VAULT_MOCK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def register_reparation_intent(dao: "MockDAO", summary: str, case_ref: str = "") -> None:
    if not reparation_vault_mock_enabled():
        return
    ref = (case_ref or "")[:120]
    msg = f"ReparationVault(mock): intent | ref={ref} | {summary[:600]}"
    dao.register_audit("incident", msg)


def maybe_register_reparation_after_mock_court(
    dao: "MockDAO",
    mock_court: Optional[Dict[str, Any]],
    case_uuid: str,
) -> None:
    """V11 Phase 3 + hub: after simulated tribunal JSON, log reparation pipeline intent."""
    if not mock_court:
        return
    register_reparation_intent(
        dao,
        "Escalation mock tribunal complete "
        f"verdict={mock_court.get('verdict_code')} "
        f"label={mock_court.get('verdict_label')} "
        f"proposal={mock_court.get('proposal_id')}",
        case_ref=(case_uuid or "")[:80],
    )
