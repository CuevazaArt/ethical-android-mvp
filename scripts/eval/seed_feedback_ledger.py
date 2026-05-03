"""V2.132: seed the feedback ledger with synthetic guided turns.

The Bayesian `posterior_assisted` path shipped in V2.124 is correct in
infrastructure but starts from an empty ledger, so the nudge effect is
invisible. This script generates a small, deterministic, guided dataset
(default 50 turns over a handful of actions) so an operator can see the
posterior bias move within its [-0.10, +0.10] cap end-to-end.

The seed is purely synthetic — every event is tagged
`source: "synthetic_seed_v1"` so it can be filtered out of any later
real-operator analysis. The script writes JSONL to a target ledger path
(default `docs/collaboration/evidence/FEEDBACK_LEDGER_SYNTHETIC_SEED.jsonl`)
and emits a small JSON summary of the resulting per-action stats and
posterior bias.

Usage::

    python scripts/eval/seed_feedback_ledger.py
    python scripts/eval/seed_feedback_ledger.py --turns 100 \\
        --output /tmp/seed.jsonl

The default output path is intentionally NOT the live
`FEEDBACK_CALIBRATION_LEDGER.jsonl` so re-running the seed never pollutes
real operator feedback. Pass `--into-live-ledger` to opt in explicitly.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.feedback import FeedbackCalibrationLedger  # noqa: E402

DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "collaboration"
    / "evidence"
    / "FEEDBACK_LEDGER_SYNTHETIC_SEED.jsonl"
)
LIVE_LEDGER = (
    ROOT / "docs" / "collaboration" / "evidence" / "FEEDBACK_CALIBRATION_LEDGER.jsonl"
)


@dataclass(frozen=True)
class GuidedAction:
    name: str
    # Probability of an UP (+1) thumb. Down is the complement.
    p_up: float


# Five canonical actions exercised by the desktop chat. The probabilities
# are deliberately spread so that the resulting posterior bias is visibly
# non-uniform — some actions saturate the +0.10 cap, others end neutral
# or slightly negative — which is exactly what an operator wants to see
# when validating the nudge end-to-end.
GUIDED_ACTIONS: tuple[GuidedAction, ...] = (
    GuidedAction("comfort_user", p_up=0.90),
    GuidedAction("share_information", p_up=0.70),
    GuidedAction("ask_clarifying_question", p_up=0.50),
    GuidedAction("decline_request", p_up=0.30),
    GuidedAction("escalate_to_human", p_up=0.10),
)


def build_seed_events(
    *,
    turns: int,
    seed: int,
    actions: tuple[GuidedAction, ...] = GUIDED_ACTIONS,
    started_at: datetime | None = None,
) -> list[dict[str, object]]:
    """Return `turns` synthetic feedback events. Pure function, no I/O."""

    if turns <= 0:
        raise ValueError("turns must be > 0")
    if not actions:
        raise ValueError("actions must be non-empty")
    rng = random.Random(seed)
    base = started_at or datetime(2026, 5, 2, 12, 0, tzinfo=UTC)
    events: list[dict[str, object]] = []
    for i in range(turns):
        action = actions[i % len(actions)]
        signal = 1 if rng.random() < action.p_up else -1
        ts = base.replace().timestamp() + i
        events.append(
            {
                "turn_id": f"seed-{i:04d}",
                "action": action.name,
                "signal": signal,
                "weights_at_time": [0.40, 0.35, 0.25],
                "captured_at": (
                    datetime.fromtimestamp(ts, tz=UTC)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                "source": "synthetic_seed_v1",
            }
        )
    return events


def write_seed_jsonl(events: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fp:
        for event in events:
            fp.write(json.dumps(event, ensure_ascii=True) + "\n")


def summarize_seed(events: list[dict[str, object]]) -> dict[str, object]:
    """Replay the seed through `FeedbackCalibrationLedger` to compute stats.

    Uses an in-memory ledger backed by a temporary path so the summary
    stays a pure derivation of the events list (the tmp file is deleted
    when the context manager exits).
    """

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "ledger.jsonl"
        ledger = FeedbackCalibrationLedger(path=tmp_path)
        for event in events:
            ledger.record(
                turn_id=str(event["turn_id"]),
                action=str(event["action"]),
                signal=int(event["signal"]),
                weights_at_time=list(event.get("weights_at_time", [])),
            )
        all_stats = ledger.stats()
        bias_per_action = {
            action: {
                "up": int(slot["up"]),
                "down": int(slot["down"]),
                "posterior_bias": ledger.posterior_bias(action),
            }
            for action, slot in all_stats.items()
        }
    return {
        "schema": "feedback_ledger_seed_summary",
        "schema_version": "1",
        "total_events": len(events),
        "actions": bias_per_action,
        "notes": (
            "Synthetic seed used to demonstrate the posterior_assisted nudge "
            "end-to-end. Every event carries source='synthetic_seed_v1' so "
            "it can be filtered out of real-operator analysis."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Seed the feedback ledger with synthetic guided turns to show "
            "the Bayesian posterior_assisted nudge end-to-end."
        )
    )
    parser.add_argument("--turns", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260502)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--into-live-ledger",
        action="store_true",
        help=(
            "Also append the synthetic events to the live "
            "FEEDBACK_CALIBRATION_LEDGER.jsonl. Off by default to keep "
            "real-operator data uncontaminated."
        ),
    )
    args = parser.parse_args()

    events = build_seed_events(turns=args.turns, seed=args.seed)
    write_seed_jsonl(events, args.output)
    summary = summarize_seed(events)

    if args.into_live_ledger:
        live_ledger = FeedbackCalibrationLedger(path=LIVE_LEDGER)
        for event in events:
            live_ledger.record(
                turn_id=str(event["turn_id"]),
                action=str(event["action"]),
                signal=int(event["signal"]),
                weights_at_time=list(event.get("weights_at_time", [])),
            )

    summary_path = args.output.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        output_display = args.output.resolve().relative_to(ROOT).as_posix()
        summary_display = summary_path.resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        output_display = args.output.name
        summary_display = summary_path.name
    print(
        json.dumps(
            {
                "ok": True,
                "events": len(events),
                "output": output_display,
                "summary": summary_display,
                "into_live_ledger": bool(args.into_live_ledger),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
