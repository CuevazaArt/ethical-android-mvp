"""
ReparationVault (MVP mock) — intended DAO treasury for third-party indemnification.

Registers **intent** lines on the audit ledger; maintains a minimal **in-process**
case table for demos (not balances or transfers). After V11 **mock escalation
tribunal** (``run_mock_escalation_court``), optionally records a reparation review
line when ``KERNEL_REPARATION_VAULT_MOCK`` is on.

Audit lines prefix ``ReparationVaultV1:`` + JSON for machine-readable parsing.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .mock_dao import MockDAO

VAULT_SCHEMA = "ReparationVaultV1"

# case_ref -> {"state": str, "events": [...]}
_case_store: Dict[str, Dict[str, Any]] = {}

STATE_INTENT = "intent_recorded"
STATE_POST_TRIBUNAL = "pending_human_review"


def reparation_vault_mock_enabled() -> bool:
    v = os.environ.get("KERNEL_REPARATION_VAULT_MOCK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _normalize_ref(case_ref: str) -> str:
    return (case_ref or "").strip()[:120] or "_default"


def get_reparation_case(case_ref: str) -> Optional[Dict[str, Any]]:
    """Return a copy of the mock case record, or None."""
    key = _normalize_ref(case_ref)
    if key not in _case_store:
        return None
    return json.loads(json.dumps(_case_store[key]))


def list_reparation_case_refs() -> List[str]:
    """Stable order for tests / operators."""
    return sorted(_case_store.keys())


def _append_event(case_ref: str, state: str, detail: str = "") -> None:
    key = _normalize_ref(case_ref)
    if key not in _case_store:
        _case_store[key] = {"state": state, "events": []}
    _case_store[key]["state"] = state
    _case_store[key]["events"].append({"state": state, "detail": detail[:600]})


def clear_reparation_vault_cases_for_tests() -> None:
    """Tests only — reset mock ledger."""
    _case_store.clear()


def register_reparation_intent(dao: "MockDAO", summary: str, case_ref: str = "") -> None:
    if not reparation_vault_mock_enabled():
        return
    ref = _normalize_ref(case_ref)
    _append_event(ref, STATE_INTENT, summary[:600])
    payload = {
        "schema": VAULT_SCHEMA,
        "case_ref": ref,
        "state": STATE_INTENT,
        "summary_excerpt": summary[:600],
    }
    msg = f"ReparationVaultV1:{json.dumps(payload, ensure_ascii=False, sort_keys=True)}"
    dao.register_audit("incident", msg[:8000])


def maybe_register_reparation_after_mock_court(
    dao: "MockDAO",
    mock_court: Optional[Dict[str, Any]],
    case_uuid: str,
) -> None:
    """V11 Phase 3 + hub: after simulated tribunal JSON, log reparation pipeline intent."""
    if not mock_court:
        return
    ref = _normalize_ref(case_uuid)
    detail = (
        f"verdict={mock_court.get('verdict_code')} "
        f"label={mock_court.get('verdict_label')} "
        f"proposal={mock_court.get('proposal_id')}"
    )
    _append_event(ref, STATE_POST_TRIBUNAL, detail)
    payload = {
        "schema": VAULT_SCHEMA,
        "case_ref": ref,
        "state": STATE_POST_TRIBUNAL,
        "mock_court": {
            "verdict_code": mock_court.get("verdict_code"),
            "verdict_label": mock_court.get("verdict_label"),
            "proposal_id": mock_court.get("proposal_id"),
        },
    }
    human = "Escalation mock tribunal complete " + detail
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    dao.register_audit("incident", f"{human} | ReparationVaultV1:{blob}"[:8000])
