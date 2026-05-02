from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def maintenance_commands() -> list[list[str]]:
    """Ordered operator commands for daily/weekly gate hygiene (no secrets)."""
    root = _repo_root()
    py = sys.executable
    evidence = root / "docs" / "collaboration" / "evidence"
    return [
        [py, str(root / "scripts" / "eval" / "record_g3_daily_contract_run.py")],
        [
            py,
            str(root / "scripts" / "eval" / "g2_transition_guard.py"),
            "--provisional-report",
            str(evidence / "G2_PROVISIONAL_LATENCY_REPORT.json"),
            "--preflight-report",
            str(evidence / "PERCEPTION_HARDWARE_PREFLIGHT.json"),
            "--live-samples",
            str(evidence / "VOICE_TURN_LATENCY_SAMPLES.jsonl"),
            "--output",
            str(evidence / "G2_TRANSITION_READINESS.json"),
        ],
        [
            py,
            str(root / "scripts" / "eval" / "desktop_gate_runner.py"),
            "snapshot",
            "--evidence-dir",
            str(evidence),
        ],
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print or run the gate maintenance command sequence (G3 daily, G2 transition, snapshot).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run each command in order (default: print only).",
    )
    args = parser.parse_args()

    for cmd in maintenance_commands():
        line = subprocess.list2cmdline(cmd)
        print(line)
        if args.execute:
            completed = subprocess.run(cmd, check=False, cwd=_repo_root())
            if completed.returncode != 0:
                return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
