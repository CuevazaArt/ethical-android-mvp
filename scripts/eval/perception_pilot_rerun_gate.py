from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.perception_pilot_evidence_validator import evaluate_evidence


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object payload.")
    return payload


def evaluate_rerun_gate(*, preflight: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    evidence_report = evaluate_evidence(evidence)
    preflight_ready = bool(preflight.get("preflight_ready", False))
    decision = str(evidence_report.get("computed_decision", "NO-GO"))
    gate_pass = preflight_ready and evidence_report["decision_matches"] and decision in {
        "GO",
        "GO-WITH-CONSTRAINTS",
    }
    return {
        "preflight_ready": preflight_ready,
        "evidence": evidence_report,
        "computed_decision": decision,
        "gate_pass": gate_pass,
        "status": "PASS" if gate_pass else "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate perception pilot physical rerun gate (105.3)."
    )
    parser.add_argument(
        "--preflight",
        type=Path,
        default=Path("docs/collaboration/evidence/PERCEPTION_HARDWARE_PREFLIGHT.json"),
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("docs/collaboration/evidence/PERCEPTION_PILOT_1_PHYSICAL_RUN.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/collaboration/evidence/PERCEPTION_PILOT_RERUN_GATE_REPORT.json"),
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Return non-zero unless rerun gate status is PASS.",
    )
    args = parser.parse_args()

    preflight = _read_json(args.preflight)
    evidence = _read_json(args.evidence)
    report = evaluate_rerun_gate(preflight=preflight, evidence=evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if args.require_pass and not bool(report["gate_pass"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
