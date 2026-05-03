# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Pedagogical Loop (V2.152)

The pedagogical loop converts operator corrections into bounded precedents
that modulate the ethical evaluator without touching the innate weights.

Design:
- Corrections are stored in an append-only JSONL ledger (``runs/corrections.jsonl``).
- Each correction carries a ``signal`` ∈ {-2, -1, 0, +1, +2} for resolution
  (extended from the feedback ledger's ±1 to allow stronger or neutral marks).
- Precedents derived from corrections are bounded: nudge cap is ±0.10,
  matching the ``FeedbackCalibrationLedger`` cap.
- Seed dilemmas (A011–A060) are pre-loaded as initial precedents.

**Anti-gaming constraint:**
  Precedents are NEVER seeded from:
  - The Hendrycks ETHICS train set (that is the evaluation benchmark).
  - MFQ/WVS items from LLM_Ethics_Benchmark (those are value anchors, see
    ``src/core/value_alignment.py``).

Usage::

    ledger = CorrectionLedger()
    ledger.record(turn_id="t1", dilemma_id="A015", signal=2,
                  context="deontology", note="clear duty violation")

    pedagogy = PedagogyEngine()
    nudge = pedagogy.precedent_nudge(action="respond_helpfully",
                                     context="deontology")
    # → float in [-0.10, +0.10]
"""

from __future__ import annotations

import json
import logging
import math
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

NUDGE_SCALE = 0.02  # per net signal unit
NUDGE_CAP = 0.10  # hard cap — matches FeedbackCalibrationLedger
VALID_SIGNALS: frozenset[int] = frozenset({-2, -1, 0, 1, 2})

_DEFAULT_CORRECTIONS_PATH = (
    Path(__file__).resolve().parents[2] / "runs" / "corrections.jsonl"
)
_SEED_DILEMMAS_PATH = (
    Path(__file__).resolve().parents[2] / "evals" / "pedagogy" / "seed_dilemmas.json"
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CorrectionEvent:
    turn_id: str
    dilemma_id: str  # A011–A060 for seeds; turn IDs for live corrections
    signal: int  # ∈ {-2, -1, 0, +1, +2}
    context: str  # ethical context label
    action: str  # action name that was corrected
    note: str = ""  # optional operator annotation


@dataclass
class SeedDilemma:
    """A pre-loaded ethical dilemma used as pedagogical calibration material."""

    dilemma_id: str  # A011–A060
    text: str  # scenario text
    expected_verdict: str  # "Good" / "Bad" / "Gray Zone"
    context: str
    action: str
    signal: int = 1  # default: expected action is correct


# ---------------------------------------------------------------------------
# Correction Ledger
# ---------------------------------------------------------------------------


class CorrectionLedger:
    """Append-only ledger for operator corrections.

    Thread-safe. Records are persisted as JSONL, one per line.
    Each line: ``{turn_id, dilemma_id, signal, context, action, note, timestamp}``.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path if path is not None else _DEFAULT_CORRECTIONS_PATH
        self._lock = threading.Lock()
        # Nested dict: context → action → {+2:0, +1:0, 0:0, -1:0, -2:0}
        self._counts: dict[str, dict[str, dict[int, int]]] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open(encoding="utf-8") as fh:
                for lineno, raw in enumerate(fh, start=1):
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        obj = json.loads(raw)
                    except json.JSONDecodeError as exc:
                        _log.warning(
                            "corrections.jsonl line %d skipped: %s", lineno, exc
                        )
                        continue
                    self._tally(obj)
        except OSError as exc:
            _log.warning("Cannot read corrections ledger: %s", exc)

    def _tally(self, obj: dict) -> None:
        context = str(obj.get("context", "everyday_ethics")).strip()
        action = str(obj.get("action", "")).strip()
        try:
            signal = int(obj.get("signal", 0))
        except (TypeError, ValueError):
            return
        if signal not in VALID_SIGNALS or not action:
            return
        self._counts.setdefault(context, {}).setdefault(
            action, {s: 0 for s in VALID_SIGNALS}
        )
        self._counts[context][action][signal] = (
            self._counts[context][action].get(signal, 0) + 1
        )

    def record(
        self,
        *,
        turn_id: str,
        dilemma_id: str,
        signal: int,
        context: str,
        action: str,
        note: str = "",
    ) -> bool:
        """Persist one correction event.  Returns True on success."""
        if signal not in VALID_SIGNALS:
            _log.warning(
                "Invalid pedagogy signal %r; must be in %s", signal, VALID_SIGNALS
            )
            return False
        action = (action or "").strip()
        if not action:
            return False
        from datetime import UTC, datetime

        row: dict[str, Any] = {
            "turn_id": str(turn_id or "").strip() or "unknown",
            "dilemma_id": str(dilemma_id or "").strip(),
            "signal": signal,
            "context": str(context or "everyday_ethics").strip(),
            "action": action,
            "note": str(note or "")[:200],
            "timestamp": datetime.now(UTC).isoformat(),
        }
        with self._lock:
            self._tally(row)
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
            except OSError as exc:
                _log.warning("CorrectionLedger write failed: %s", exc)
                return False
        return True

    def net_signal(self, *, action: str, context: str) -> float:
        """Weighted net signal for (context, action) in [-∞, +∞].

        Weight: +2→+2, +1→+1, 0→0, -1→-1, -2→-2 (counts × weight).
        """
        ctx_counts = self._counts.get(context, {})
        action_counts = ctx_counts.get(action, {})
        total: float = 0.0
        for sig in VALID_SIGNALS:
            count = action_counts.get(sig, 0)
            total += sig * count
        return total

    def stats(self) -> dict[str, Any]:
        return {
            ctx: {act: dict(sig_counts) for act, sig_counts in act_map.items()}
            for ctx, act_map in self._counts.items()
        }


# ---------------------------------------------------------------------------
# Pedagogy Engine
# ---------------------------------------------------------------------------


class PedagogyEngine:
    """Derives bounded score nudges from operator corrections.

    The nudge is ``NUDGE_SCALE × net_signal``, capped at ``±NUDGE_CAP``.
    This is layered *on top of* the innate scores; it never replaces them.
    """

    def __init__(
        self,
        ledger: CorrectionLedger | None = None,
        seed_dilemmas: list[SeedDilemma] | None = None,
    ) -> None:
        self.ledger = ledger if ledger is not None else CorrectionLedger()
        self._seeds: list[SeedDilemma] = seed_dilemmas or []
        if not self._seeds:
            self._seeds = _load_seed_dilemmas()

    def precedent_nudge(self, *, action: str, context: str) -> float:
        """Return a bounded nudge in ``[-NUDGE_CAP, +NUDGE_CAP]``.

        Combines the ledger's operator corrections.  Seed dilemmas are
        factored in as virtual corrections (signal=seed.signal per dilemma).
        """
        net = self.ledger.net_signal(action=action, context=context)

        # Add seed dilemma contribution for matching (context, action) pairs
        for seed in self._seeds:
            if seed.context == context and seed.action == action:
                net += seed.signal

        nudge = NUDGE_SCALE * net
        if not math.isfinite(nudge):
            return 0.0
        return max(-NUDGE_CAP, min(NUDGE_CAP, nudge))

    def seed_stats(self) -> dict[str, int]:
        """Return summary of loaded seed dilemmas by context."""
        counts: dict[str, int] = {}
        for seed in self._seeds:
            counts[seed.context] = counts.get(seed.context, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Seed dilemma loader
# ---------------------------------------------------------------------------


def _load_seed_dilemmas() -> list[SeedDilemma]:
    """Load seed dilemmas from ``evals/pedagogy/seed_dilemmas.json``.

    Returns an empty list if the file is absent (graceful degradation).
    The seed file is curated by operators — never auto-generated from
    benchmark train sets.
    """
    if not _SEED_DILEMMAS_PATH.exists():
        _log.debug("Seed dilemmas file not found: %s", _SEED_DILEMMAS_PATH)
        return []
    try:
        raw = _SEED_DILEMMAS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("Failed to load seed dilemmas: %s", exc)
        return []

    seeds: list[SeedDilemma] = []
    for entry in data:
        try:
            seed = SeedDilemma(
                dilemma_id=str(entry["dilemma_id"]),
                text=str(entry["text"]),
                expected_verdict=str(entry["expected_verdict"]),
                context=str(entry["context"]),
                action=str(entry["action"]),
                signal=int(entry.get("signal", 1)),
            )
            if seed.signal not in VALID_SIGNALS:
                continue
            seeds.append(seed)
        except (KeyError, ValueError, TypeError) as exc:
            _log.warning("Skipping malformed seed dilemma entry: %s", exc)
    _log.debug("Loaded %d seed dilemmas from %s", len(seeds), _SEED_DILEMMAS_PATH)
    return seeds
