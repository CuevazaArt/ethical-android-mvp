"""
Machine-readable kernel decision events (stderr JSON lines when enabled).

Requires ``KERNEL_LOG_JSON=1``. Optional ``KERNEL_LOG_DECISION_EVENTS`` (default **on** when JSON
logs are on) emits one JSON object per ``EthicalKernel.process`` completion with no secrets.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from .context import request_id_var

logger = logging.getLogger("ethos.kernel.decision")


def decision_log_enabled() -> bool:
    if os.environ.get("KERNEL_LOG_JSON", "").strip().lower() not in ("1", "true", "yes", "on"):
        return False
    raw = os.environ.get("KERNEL_LOG_DECISION_EVENTS", "1").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    return True


def log_kernel_decision_event(d: Any, latency_s: float) -> None:
    """
    Emit a single JSON line (via log message body) for log aggregators.

    Fields are bounded; ``final_action`` is truncated. Omits full pole breakdown to limit size.
    """
    if not decision_log_enabled():
        return
    rid = request_id_var.get()
    payload: dict[str, Any] = {
        "event": "kernel_decision",
        "latency_ms": round(max(0.0, latency_s) * 1000.0, 4),
        "blocked": bool(getattr(d, "blocked", False)),
        "decision_mode": str(getattr(d, "decision_mode", "")),
        "final_action": str(getattr(d, "final_action", ""))[:500],
        "scenario": str(getattr(d, "scenario", ""))[:300],
    }
    if rid:
        payload["request_id"] = rid
    br = getattr(d, "bayesian_result", None)
    if br is not None:
        payload["uncertainty"] = round(float(br.uncertainty), 6)
        payload["expected_impact"] = round(float(br.expected_impact), 6)
    mo = getattr(d, "moral", None)
    if mo is not None:
        payload["verdict"] = str(mo.global_verdict.value)
        payload["moral_total_score"] = round(float(mo.total_score), 6)
    logger.info(json.dumps(payload, ensure_ascii=False))
