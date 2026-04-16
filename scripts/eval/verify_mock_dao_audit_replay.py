"""Verify MockDAO audit ledger fingerprints (DJ-BL-01). Compare two JSON exports or print one hash.

For merge-conflict replay artifacts paired with a ``lan_governance`` export, see
``scripts/eval/verify_lan_governance_replay_sidecar.py`` (replay sidecar, DJ-BL-15).
For a single expected anchor hex vs ledger file, see ``scripts/eval/compare_audit_ledger_anchor.py`` (DJ-BL-17).
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
        description="Fingerprint MockDAO audit ledger JSON (array of rows) or compare two files",
    )
    ap.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="JSON file: array of {id,type,content,timestamp,episode_id}",
    )
    ap.add_argument(
        "--compare",
        type=Path,
        metavar="FILE2",
        help="Second JSON file; exit 0 if fingerprints match, 1 if mismatch",
    )
    args = ap.parse_args()

    if args.file is None:
        ap.print_help()
        return 2

    fp1 = fingerprint_audit_ledger(_load_ledger(args.file))
    if args.compare is None:
        print(fp1)
        return 0

    fp2 = fingerprint_audit_ledger(_load_ledger(args.compare))
    if fp1 == fp2:
        print(f"match fingerprint={fp1}")
        return 0
    print(f"mismatch fp1={fp1}", file=sys.stderr)
    print(f"mismatch fp2={fp2}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
