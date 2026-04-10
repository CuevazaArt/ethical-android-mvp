"""
MLEthicsTuner (MVP stub) — expert-in-the-loop hook for gray-zone / ambiguous inference.

Does **not** change Bayesian weights. When enabled, appends a DAO audit line so
incident + gray-zone turns are traceable for future human review.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .mock_dao import MockDAO


def ml_ethics_tuner_log_enabled() -> bool:
    v = os.environ.get("KERNEL_ML_ETHICS_TUNER_LOG", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def maybe_log_gray_zone_tuning_opportunity(dao: "MockDAO", chat_result: Any) -> None:
    """If the chat turn is gray zone, register a mock expert-loop opportunity."""
    if not ml_ethics_tuner_log_enabled():
        return
    d = getattr(chat_result, "decision", None)
    if d is None:
        return
    mode = getattr(d, "decision_mode", "") or ""
    verdict = ""
    if d.moral is not None:
        verdict = str(d.moral.global_verdict.value)
    if mode != "gray_zone" and verdict != "Gray Zone":
        return
    dao.register_audit(
        "calibration",
        "MLEthicsTuner(mock): gray_zone turn eligible for expert-in-the-loop weight review (no weights changed)",
    )
