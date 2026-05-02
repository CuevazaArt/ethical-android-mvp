from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_PROVISIONAL_REPORT = Path("docs/collaboration/evidence/G2_PROVISIONAL_LATENCY_REPORT.json")
DEFAULT_PREFLIGHT_REPORT = Path("docs/collaboration/evidence/PERCEPTION_HARDWARE_PREFLIGHT.json")
DEFAULT_LIVE_SAMPLES = Path("docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl")
DEFAULT_TEXT_SAMPLES = Path("docs/collaboration/evidence/G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl")
DEFAULT_OUTPUT = Path("docs/collaboration/evidence/G2_TRANSITION_READINESS.json")


@dataclass(frozen=True)
class G2TransitionSnapshot:
    generated_at: str
    status: str
    provisional_valid: bool
    hardware_ready: bool
    live_sample_count: int
    target_live_sample_count: int
    checklist: list[str]
    notes: list[str]
    mode: str = "live"
    text_mediated_sample_count: int = 0


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def _parse_iso_utc(raw: str) -> datetime | None:
    if not raw.strip():
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _to_iso_utc(raw: datetime) -> str:
    return raw.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _is_finite_non_negative(value: Any) -> bool:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(parsed) and parsed >= 0.0


def _provisional_is_valid(payload: dict[str, Any], *, now: datetime, max_age_days: int) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if not payload:
        notes.append("missing provisional latency report")
        return False, notes
    if not bool(payload.get("provisional")):
        notes.append("report does not declare provisional=true")
        return False, notes
    if not _is_finite_non_negative(payload.get("p95_ms")):
        notes.append("report p95_ms is missing or non-finite")
        return False, notes
    if not _is_finite_non_negative(payload.get("target_p95_ms")):
        notes.append("report target_p95_ms is missing or non-finite")
        return False, notes
    generated_at = _parse_iso_utc(str(payload.get("generated_at", "")))
    if generated_at is None:
        notes.append("report generated_at is missing or invalid")
        return False, notes
    max_age = timedelta(days=max_age_days)
    if now - generated_at > max_age:
        notes.append(f"provisional report is stale (> {max_age_days} days)")
        return False, notes
    notes.append("provisional report is valid and fresh")
    return True, notes


def _hardware_ready(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    notes: list[str] = []
    if not payload:
        notes.append("missing hardware preflight report")
        return False, notes
    if bool(payload.get("preflight_ready")):
        notes.append("preflight_ready=true")
        return True, notes
    camera_count = int(payload.get("summary", {}).get("camera_count", 0))
    mic_count = int(payload.get("summary", {}).get("microphone_count", 0))
    notes.append(f"preflight_ready=false (camera_count={camera_count}, microphone_count={mic_count})")
    return False, notes


def _valid_live_sample_count(samples_path: Path) -> int:
    rows = _read_jsonl(samples_path)
    valid = 0
    for row in rows:
        if not _is_finite_non_negative(row.get("total_ms")):
            continue
        captured_at = _parse_iso_utc(str(row.get("captured_at", "")))
        if captured_at is None:
            continue
        valid += 1
    return valid


def evaluate_transition(
    *,
    provisional_report_path: Path = DEFAULT_PROVISIONAL_REPORT,
    preflight_report_path: Path = DEFAULT_PREFLIGHT_REPORT,
    live_samples_path: Path = DEFAULT_LIVE_SAMPLES,
    text_mediated_samples_path: Path = DEFAULT_TEXT_SAMPLES,
    max_provisional_age_days: int = 14,
    target_live_sample_count: int = 20,
    now: datetime | None = None,
) -> G2TransitionSnapshot:
    clock = now or datetime.now(UTC)
    provisional_report = _read_json(provisional_report_path)
    preflight_report = _read_json(preflight_report_path)
    provisional_valid, provisional_notes = _provisional_is_valid(
        provisional_report,
        now=clock,
        max_age_days=max_provisional_age_days,
    )
    hardware_ready, hardware_notes = _hardware_ready(preflight_report)
    live_sample_count = _valid_live_sample_count(live_samples_path)
    text_sample_count = _valid_live_sample_count(text_mediated_samples_path)

    checklist = [
        "keep G2 as in_progress while evidence remains provisional",
        "collect live hardware latency samples with capture_voice_turn_latency.py",
        "refresh gate snapshot after live sample capture",
    ]

    mode = "live"
    # V2.127 (B1): text_mediated path unblocks G2 progression even when audio
    # hardware is unavailable. Treat it as the dominant path when there are
    # enough text-mediated samples on disk; otherwise fall back to the live
    # hardware ladder.
    if text_sample_count >= target_live_sample_count:
        mode = "text_mediated"
        status = "READY_FOR_LIVE_EVALUATION"
        checklist.insert(
            1,
            "run desktop_gate_runner.py latency on G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl",
        )
    elif not provisional_valid:
        status = "BLOCKED_PROVISIONAL_MISSING"
        checklist.insert(1, "regenerate provisional report with g2_synthetic_latency_harness.py")
    elif not hardware_ready:
        status = "BLOCKED_HARDWARE"
        checklist.insert(
            1,
            (
                "unblock hardware and rerun perception_hardware_preflight.py, "
                "or capture text_mediated samples with capture_voice_turn_latency_text.py"
            ),
        )
    elif live_sample_count < target_live_sample_count:
        status = "READY_FOR_LIVE_CAPTURE"
        checklist.insert(1, f"capture at least {target_live_sample_count} live samples")
    else:
        status = "READY_FOR_LIVE_EVALUATION"
        checklist.insert(1, "run desktop_gate_runner.py latency using live samples")

    notes = provisional_notes + hardware_notes + [
        f"live_sample_count={live_sample_count}",
        f"text_mediated_sample_count={text_sample_count}",
        f"target_live_sample_count={target_live_sample_count}",
        f"mode={mode}",
    ]
    return G2TransitionSnapshot(
        generated_at=_to_iso_utc(clock),
        status=status,
        provisional_valid=provisional_valid,
        hardware_ready=hardware_ready,
        live_sample_count=live_sample_count,
        target_live_sample_count=target_live_sample_count,
        checklist=checklist,
        notes=notes,
        mode=mode,
        text_mediated_sample_count=text_sample_count,
    )


def write_report(path: Path, snapshot: G2TransitionSnapshot) -> None:
    payload = {
        "generated_at": snapshot.generated_at,
        "status": snapshot.status,
        "mode": snapshot.mode,
        "provisional_valid": snapshot.provisional_valid,
        "hardware_ready": snapshot.hardware_ready,
        "live_sample_count": snapshot.live_sample_count,
        "text_mediated_sample_count": snapshot.text_mediated_sample_count,
        "target_live_sample_count": snapshot.target_live_sample_count,
        "checklist": snapshot.checklist,
        "notes": snapshot.notes,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate G2 transition readiness from provisional to live hardware evidence.",
    )
    parser.add_argument("--provisional-report", type=Path, default=DEFAULT_PROVISIONAL_REPORT)
    parser.add_argument("--preflight-report", type=Path, default=DEFAULT_PREFLIGHT_REPORT)
    parser.add_argument("--live-samples", type=Path, default=DEFAULT_LIVE_SAMPLES)
    parser.add_argument(
        "--text-mediated-samples", type=Path, default=DEFAULT_TEXT_SAMPLES
    )
    parser.add_argument("--max-provisional-age-days", type=int, default=14)
    parser.add_argument("--target-live-sample-count", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    snapshot = evaluate_transition(
        provisional_report_path=args.provisional_report,
        preflight_report_path=args.preflight_report,
        live_samples_path=args.live_samples,
        text_mediated_samples_path=args.text_mediated_samples,
        max_provisional_age_days=args.max_provisional_age_days,
        target_live_sample_count=args.target_live_sample_count,
    )
    write_report(args.output, snapshot)
    print(
        json.dumps(
            {
                "gate": "G2",
                "status": snapshot.status,
                "mode": snapshot.mode,
                "provisional_valid": snapshot.provisional_valid,
                "hardware_ready": snapshot.hardware_ready,
                "live_sample_count": snapshot.live_sample_count,
                "text_mediated_sample_count": snapshot.text_mediated_sample_count,
                "target_live_sample_count": snapshot.target_live_sample_count,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0 if snapshot.status in {"READY_FOR_LIVE_CAPTURE", "READY_FOR_LIVE_EVALUATION"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
