"""
MLEthicsTuner (MVP stub) — expert-in-the-loop hook for gray-zone / ambiguous inference.

Does **not** change Bayesian weights. When enabled, appends a DAO audit line with a
**structured JSON** payload (parseable; schema versioned) so gray-zone turns are
traceable for future human review.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .mock_dao import MockDAO

EVENT_SCHEMA = "MLEthicsTunerEventV1"


def ml_ethics_tuner_log_enabled() -> bool:
    v = os.environ.get("KERNEL_ML_ETHICS_TUNER_LOG", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _fingerprint(
    decision_mode: str,
    verdict: str,
    final_action: str,
    episode_id: str,
) -> str:
    raw = f"{decision_mode}|{verdict}|{final_action}|{episode_id}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def build_gray_zone_event_payload(
    chat_result: Any,
    *,
    kernel: Any = None,
) -> Optional[Dict[str, Any]]:
    """Build structured dict if this turn qualifies for expert-loop logging."""
    d = getattr(chat_result, "decision", None)
    if d is None:
        return None
    mode = getattr(d, "decision_mode", "") or ""
    verdict = ""
    if d.moral is not None:
        verdict = str(d.moral.global_verdict.value)
    if mode != "gray_zone" and verdict != "Gray Zone":
        return None
    final_action = getattr(d, "final_action", "") or ""
    ep_id = ""
    if kernel is not None:
        ep_id = str(getattr(kernel, "_last_registered_episode_id", "") or "")
    return {
        "schema": EVENT_SCHEMA,
        "decision_mode": mode,
        "global_verdict": verdict,
        "final_action": final_action,
        "episode_id": ep_id,
        "content_sha256_short": _fingerprint(mode, verdict, final_action, ep_id),
        "note": "expert-in-the-loop review eligible; Bayesian weights unchanged",
    }


def maybe_log_gray_zone_tuning_opportunity(
    dao: "MockDAO",
    chat_result: Any,
    *,
    kernel: Any = None,
) -> None:
    """If the chat turn is gray zone, register a mock expert-loop opportunity."""
    if not ml_ethics_tuner_log_enabled():
        return
    payload = build_gray_zone_event_payload(chat_result, kernel=kernel)
    if payload is None:
        return
    line = "MLEthicsTuner: " + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    dao.register_audit(
        "calibration",
        line[:8000],
    )
