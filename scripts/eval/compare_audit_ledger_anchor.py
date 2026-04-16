"""Compare a MockDAO audit ledger export to an expected SHA-256 fingerprint (Phase 3 stub).

This is an **operator checkpoint** helper: pass the JSON array file and the hex digest you expect
from an off-chain anchor or prior run. It does **not** talk to a chain.

See ``docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`` (Phase 3).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.modules.mock_dao_audit_replay import fingerprint_audit_ledger  # noqa: E402


def _load_ledger(path: Path) -> list[dict[str, object]]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("expected JSON array of audit rows")
    return list(data)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Exit 0 if audit ledger JSON fingerprint matches expected hex",
    )
    ap.add_argument("ledger", type=Path, help="JSON array of audit rows")
    ap.add_argument(
        "expected_hex",
        help="Expected SHA-256 fingerprint (64 hex chars)",
    )
    args = ap.parse_args()

    exp = str(args.expected_hex).strip().lower()
    if len(exp) != 64 or any(c not in "0123456789abcdef" for c in exp):
        print("error: expected_hex must be 64 lowercase hex characters", file=sys.stderr)
        return 2

    fp = fingerprint_audit_ledger(_load_ledger(args.ledger)).lower()
    if fp == exp:
        print("match")
        return 0
    print(f"mismatch actual={fp}", file=sys.stderr)
    print(f"mismatch expect={exp}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
