from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_KEYS = (
    "run_metadata",
    "input_conditions",
    "core_metrics",
    "incidents",
    "decision",
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Evidence payload must be a JSON object.")
    return payload


def _incident_severity(incident: dict[str, Any]) -> str:
    severity = str(incident.get("severity", "")).strip().upper()
    return severity if severity in {"HIGH", "MED", "LOW"} else "LOW"


def _compute_decision(payload: dict[str, Any]) -> str:
    core = payload.get("core_metrics", {})
    incidents = payload.get("incidents", [])
    if not isinstance(core, dict):
        return "NO-GO"
    if not isinstance(incidents, list):
        return "NO-GO"

    rollback_pass = bool(core.get("rollback_pass", False))
    latency_within_target = bool(core.get("latency_within_target", False))
    capture_disconnect_count = int(core.get("capture_disconnect_count", 0))
    mitigation_owner = str(payload.get("decision", {}).get("next_action_owner", "")).strip()

    severities = [_incident_severity(item) for item in incidents if isinstance(item, dict)]
    high_count = sum(1 for sev in severities if sev == "HIGH")
    med_count = sum(1 for sev in severities if sev == "MED")

    if (
        high_count == 0
        and med_count == 0
        and capture_disconnect_count == 0
        and rollback_pass
        and latency_within_target
    ):
        return "GO"

    if (
        high_count == 0
        and med_count == 1
        and rollback_pass
        and latency_within_target
        and bool(mitigation_owner)
    ):
        return "GO-WITH-CONSTRAINTS"

    return "NO-GO"


def evaluate_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    missing_keys = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in payload]
    declared_decision = str(payload.get("decision", {}).get("result", "")).strip().upper()
    if declared_decision not in {"GO", "GO-WITH-CONSTRAINTS", "NO-GO"}:
        declared_decision = "UNKNOWN"

    computed_decision = _compute_decision(payload)
    return {
        "missing_keys": missing_keys,
        "declared_decision": declared_decision,
        "computed_decision": computed_decision,
        "decision_matches": declared_decision == computed_decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate perception pilot evidence payload and decision rubric."
    )
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument(
        "--require-decision-match",
        action="store_true",
        help="Return non-zero when declared decision doesn't match computed rubric decision.",
    )
    args = parser.parse_args()

    payload = _read_json(args.evidence)
    report = evaluate_evidence(payload)
    print(json.dumps(report, ensure_ascii=True, indent=2))

    has_missing = len(report["missing_keys"]) > 0
    if has_missing:
        return 1
    if args.require_decision_match and not report["decision_matches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
