"""V2.124 (C2): minimal feedback ledger and posterior-assisted bias.

The historical `FeedbackCalibrationLedger` was pruned during the V2 cleanup
sweeps. This module re-implements the smallest surface required by the
desktop chat path:

- Append-only JSONL ledger of `{turn_id, action, signal, weights_at_time}`
  events with thread-safe writes.
- A `posterior_bias(action)` helper that returns a small, capped score
  adjustment derived from the (up - down) net for that action.
- A boolean `is_posterior_assisted_enabled()` reading the
  `KERNEL_BAYESIAN_MODE` environment variable.

The bias is intentionally conservative: 0.02 per net signal, capped at
+/- 0.10. This keeps the posterior auditable and bounded; users can never
"poison" the evaluator into producing arbitrary actions.
"""

from __future__ import annotations

import json
import os
import threading
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_LEDGER_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "collaboration"
    / "evidence"
    / "FEEDBACK_CALIBRATION_LEDGER.jsonl"
)
POSTERIOR_BIAS_SCALE = 0.02
POSTERIOR_BIAS_CAP = 0.10
POSTERIOR_ASSISTED_MODE = "posterior_assisted"

__all__ = [
    "DEFAULT_LEDGER_PATH",
    "POSTERIOR_BIAS_SCALE",
    "POSTERIOR_BIAS_CAP",
    "POSTERIOR_ASSISTED_MODE",
    "FeedbackEvent",
    "FeedbackCalibrationLedger",
    "is_posterior_assisted_enabled",
]


def is_posterior_assisted_enabled() -> bool:
    """True when `KERNEL_BAYESIAN_MODE=posterior_assisted` is set."""

    raw = os.environ.get("KERNEL_BAYESIAN_MODE", "").strip().lower()
    return raw == POSTERIOR_ASSISTED_MODE


@dataclass(frozen=True)
class FeedbackEvent:
    turn_id: str
    action: str
    signal: int  # +1 or -1
    weights_at_time: tuple[float, ...] = ()


class FeedbackCalibrationLedger:
    """Append-only ledger that derives a small posterior bias per action."""

    def __init__(self, path: Path | None = None) -> None:
        self.path: Path = path if path is not None else DEFAULT_LEDGER_PATH
        self._lock = threading.Lock()
        self._counts: dict[str, dict[int, int]] = defaultdict(lambda: {1: 0, -1: 0})
        self._load_existing()

    def _load_existing(self) -> None:
        if not self.path.exists():
            return
        try:
            for raw in self.path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                action = str(payload.get("action", "")).strip()
                try:
                    signal = int(payload.get("signal", 0))
                except (TypeError, ValueError):
                    continue
                if not action or signal not in (1, -1):
                    continue
                slot = self._counts[action]
                slot[signal] = slot.get(signal, 0) + 1
        except OSError:
            return

    def record(
        self,
        *,
        turn_id: str,
        action: str,
        signal: int,
        weights_at_time: list[float] | tuple[float, ...] | None = None,
    ) -> bool:
        """Persist a single feedback event. Returns True when stored."""

        cleaned_action = (action or "").strip()
        if signal not in (1, -1) or not cleaned_action:
            return False
        event = FeedbackEvent(
            turn_id=str(turn_id or "").strip() or "unknown",
            action=cleaned_action,
            signal=signal,
            weights_at_time=tuple(float(w) for w in (weights_at_time or [])),
        )
        with self._lock:
            slot = self._counts[event.action]
            slot[event.signal] = slot.get(event.signal, 0) + 1
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fp:
                fp.write(
                    json.dumps(
                        {
                            "turn_id": event.turn_id,
                            "action": event.action,
                            "signal": event.signal,
                            "weights_at_time": list(event.weights_at_time),
                        },
                        ensure_ascii=True,
                    )
                    + "\n"
                )
        return True

    def posterior_bias(
        self,
        action: str,
        *,
        scale: float = POSTERIOR_BIAS_SCALE,
        cap: float = POSTERIOR_BIAS_CAP,
    ) -> float:
        """Return a bounded `[-cap, +cap]` score nudge for an action."""

        slot = self._counts.get(action, {1: 0, -1: 0})
        net = int(slot.get(1, 0)) - int(slot.get(-1, 0))
        biased = float(scale) * float(net)
        if biased > cap:
            return float(cap)
        if biased < -cap:
            return float(-cap)
        return biased

    def stats(self, action: str | None = None) -> dict[str, Any]:
        if action is not None:
            slot = self._counts.get(action, {1: 0, -1: 0})
            return {
                "action": action,
                "up": int(slot.get(1, 0)),
                "down": int(slot.get(-1, 0)),
            }
        return {
            name: {"up": int(slot.get(1, 0)), "down": int(slot.get(-1, 0))}
            for name, slot in self._counts.items()
        }
