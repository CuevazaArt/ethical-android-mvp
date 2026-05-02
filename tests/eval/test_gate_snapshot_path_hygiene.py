"""V2.130: gate snapshots must store repo-relative evidence paths.

The canonical `MVP_CLOSURE_REPORT.json` and the live `build_gate_snapshot`
output are versioned artifacts read by non-author operators. Absolute paths
(`C:/Users/...`, `/home/runner/...`, `/Users/...`) leak the author's local
environment, break portability, and would be flagged by an external auditor.

This test fails fast if any `gate_snapshot.gates[*].source` ever regresses
to an absolute or backslashed form, both for the committed JSON artifact
and for fresh snapshots built from a temporary evidence directory.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from scripts.eval.desktop_gate_runner import build_gate_snapshot

REPO_ROOT = Path(__file__).resolve().parents[2]
CLOSURE_REPORT = (
    REPO_ROOT / "docs" / "collaboration" / "evidence" / "MVP_CLOSURE_REPORT.json"
)

# Anything that looks like an absolute filesystem path. Covers Windows drive
# letters, POSIX-style absolute paths, UNC shares, and explicit user-home
# prefixes that frequently leak from author machines.
_ABSOLUTE_PATH_RE = re.compile(
    r"(?:^|[\s,;\"'(])"
    r"(?:[A-Za-z]:[\\/]"  # C:\ or C:/
    r"|[\\]{2}"  # UNC \\server\share
    r"|/home/"
    r"|/Users/"
    r"|/root/"
    r"|/tmp/"
    r"|/private/var/"
    r")"
)


def _assert_relative(label: str, source: str) -> None:
    assert source, f"{label}: empty source"
    assert "\\" not in source, f"{label}: backslash in source: {source!r}"
    assert not _ABSOLUTE_PATH_RE.search(source), (
        f"{label}: absolute path leaked into snapshot source: {source!r}"
    )


def test_committed_closure_report_has_no_absolute_paths() -> None:
    payload = json.loads(CLOSURE_REPORT.read_text(encoding="utf-8"))
    gates = payload["gate_snapshot"]["gates"]
    assert gates, "closure report has no gates"
    for gate_name, gate in gates.items():
        _assert_relative(f"closure-report:{gate_name}", str(gate.get("source", "")))


def test_fresh_snapshot_from_tmp_evidence_dir_uses_relative_paths(
    tmp_path: Path,
) -> None:
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    # Seed minimum evidence so build_gate_snapshot exercises every gate
    # branch (G1 from ledger, G2 from text-mediated, G3 empty, G4 demo).
    (evidence_dir / "DESKTOP_STABILITY_LEDGER.jsonl").write_text(
        "\n".join(
            json.dumps({"date": f"2026-04-{day:02d}T09:00:00Z", "status": "pass"})
            for day in range(17, 31)
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl").write_text(
        "\n".join(
            json.dumps({"captured_at": f"2026-04-30T10:00:{i:02d}Z", "total_ms": 1.5})
            for i in range(22)
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "DEMO_RELIABILITY_CHECKLIST.json").write_text(
        json.dumps(
            {
                "run_id": "demo-reliability-20260430T120000Z",
                "items": [{"name": f"step-{i}", "passed": True} for i in range(10)],
            }
        ),
        encoding="utf-8",
    )

    snapshot = build_gate_snapshot(
        evidence_dir=evidence_dir, now=datetime(2026, 4, 30, 23, 0, tzinfo=UTC)
    )
    for gate_name, gate in snapshot["gates"].items():
        _assert_relative(f"fresh:{gate_name}", str(gate.get("source", "")))
