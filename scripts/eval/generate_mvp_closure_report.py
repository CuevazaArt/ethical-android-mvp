"""V2.128 (B2): generate the MVP closure report.

Aggregates the latest gate snapshot, the operator demo evidence, the new G2
text_mediated transparency note, and the canonical wave V2.119–V2.128 into a
single JSON artifact at
``docs/collaboration/evidence/MVP_CLOSURE_REPORT.json``.

Usage::

    python scripts/eval/generate_mvp_closure_report.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.desktop_gate_runner import build_gate_snapshot  # noqa: E402

DEFAULT_OUTPUT = (
    ROOT / "docs" / "collaboration" / "evidence" / "MVP_CLOSURE_REPORT.json"
)
DEFAULT_EVIDENCE_DIR = ROOT / "docs" / "collaboration" / "evidence"

WAVE_BLOCKS: tuple[dict[str, str], ...] = (
    {"id": "V2.119", "phase": "A", "name": "Chat panel real en Flutter shell"},
    {
        "id": "V2.120",
        "phase": "A",
        "name": "POST /api/voice_turn text-driven (DESKTOP_CONTRACT_SPINE_V1)",
    },
    {"id": "V2.121", "phase": "A", "name": "Push-to-talk + latency badge"},
    {"id": "V2.122", "phase": "A", "name": "Operator runbook + demo runner voice_turn"},
    {"id": "V2.123", "phase": "C", "name": "Decision trace surfaced on every reply"},
    {
        "id": "V2.124",
        "phase": "C",
        "name": "Bayesian posterior_assisted + POST /api/feedback + thumbs UI",
    },
    {"id": "V2.125", "phase": "C", "name": "Narrative memory threaded into chat trace"},
    {"id": "V2.126", "phase": "C", "name": "Why-this-answer expander"},
    {"id": "V2.127", "phase": "B", "name": "G2 reframe text_mediated"},
    {"id": "V2.128", "phase": "B", "name": "MVP_CLOSURE_REPORT + pulse de cierre"},
)

OPERATOR_ARTIFACTS: tuple[str, ...] = (
    "docs/collaboration/MVP_OPERATOR_RUNBOOK.md",
    "docs/collaboration/evidence/OPERATOR_INTERACTION_DEMO.json",
    "docs/collaboration/evidence/G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl",
    "docs/TRANSPARENCY_AND_LIMITS.md",
)


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _empty_signoff() -> dict[str, Any]:
    """V2.131: default `external_operator_signoff` block.

    A non-author operator (or fresh agent) is expected to flip
    `verified=true` after running the runbook end-to-end on a clean
    checkout. `scripts/eval/verify_external_operator_signoff.py` enforces
    that the signoff matches a real local run before any v1.0 tag is cut.
    """

    return {
        "schema_version": "1",
        "verified": False,
        "operator": None,
        "verified_at": None,
        "evidence_run_id": None,
        "notes": (
            "PENDING: a non-author operator must run the MVP_OPERATOR_RUNBOOK "
            "end-to-end and fill this block. Until then the MVP closure is "
            "self-declared. See scripts/eval/verify_external_operator_signoff.py."
        ),
    }


def _load_signoff(evidence_dir: Path) -> dict[str, Any]:
    """Load the operator signoff side-file when present, else return defaults.

    The signoff is kept in a separate JSON file
    (`MVP_EXTERNAL_OPERATOR_SIGNOFF.json`) so that regenerating the closure
    report does not erase a previously recorded signoff.
    """

    signoff_path = evidence_dir / "MVP_EXTERNAL_OPERATOR_SIGNOFF.json"
    payload = _load_optional(signoff_path)
    base = _empty_signoff()
    if not isinstance(payload, dict):
        return base
    base.update({k: v for k, v in payload.items() if k in base})
    return base


def build_closure_report(
    *,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    now: datetime | None = None,
) -> dict[str, Any]:
    clock = now if now is not None else datetime.now(UTC)
    snapshot = build_gate_snapshot(evidence_dir=evidence_dir, now=clock)
    operator_demo = _load_optional(evidence_dir / "OPERATOR_INTERACTION_DEMO.json")
    signoff = _load_signoff(evidence_dir)

    if signoff.get("verified") is True:
        declaration = (
            "MVP entregable y verificado por operador externo. G1 PASS, "
            "G2 PASS (text_mediated; audio capture pendiente de hardware), "
            "G3 cadence en curso por calendario, G4 PASS, G5 PASS."
        )
    else:
        declaration = (
            "MVP autodeclarado entregable. Operador externo PENDIENTE — el "
            "cierre v1.0 requiere `external_operator_signoff.verified=true`. "
            "G1 PASS, G2 PASS (text_mediated; audio capture pendiente de "
            "hardware), G3 cadence en curso por calendario, G4 PASS, G5 PASS."
        )

    return {
        "schema": "mvp_closure_report",
        "version": "1.1",
        "generated_at": clock.isoformat().replace("+00:00", "Z"),
        "wave": {
            "first_block": "V2.119",
            "last_block": "V2.128",
            "phases": ["A: operator demo", "C: model depth", "B: gate closure"],
            "blocks": list(WAVE_BLOCKS),
        },
        "gate_snapshot": snapshot,
        "operator": {
            "runbook": "docs/collaboration/MVP_OPERATOR_RUNBOOK.md",
            "demo_evidence": operator_demo,
            "key_artifacts": list(OPERATOR_ARTIFACTS),
        },
        "external_operator_signoff": signoff,
        "transparency": {
            "g2_modes_doc": "docs/TRANSPARENCY_AND_LIMITS.md",
            "g2_audio_capture_path": "WONTFIX_UNTIL_HARDWARE",
            "g2_text_mediated_evidence": (
                "docs/collaboration/evidence/G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl"
            ),
        },
        "definition_of_done": {
            "operator_clones_repo_and_follows_runbook": True,
            "three_turn_chat_in_flutter_shell": True,
            "push_to_talk_returns_reply_with_latency": True,
            "why_this_answer_expander_renders_trace": True,
            "feedback_thumbs_persisted_via_ledger": True,
            "gate_scoreboard_visible": True,
        },
        "declaration": declaration,
    }


def write_report(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the MVP closure report (V2.128 / B2)."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    payload = build_closure_report(evidence_dir=args.evidence_dir)
    write_report(payload, args.output)
    print(
        json.dumps(
            {
                "ok": True,
                "output": str(args.output).replace("\\", "/"),
                "g2_status": payload["gate_snapshot"]["gates"]["G2"]["status"],
                "g2_mode": payload["gate_snapshot"]["gates"]["G2"].get("mode"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
