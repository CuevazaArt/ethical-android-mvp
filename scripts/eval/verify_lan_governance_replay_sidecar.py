"""Verify LAN governance replay sidecar fingerprints (DJ-BL-15).

Compare two sidecar JSON files, or fingerprint one. Optionally check audit ledger hash
against a MockDAO audit export (same shape as ``verify_mock_dao_audit_replay.py``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.modules.governance.lan_governance_replay_sidecar import (  # noqa: E402
    LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1,
    fingerprint_replay_sidecar,
)
from src.modules.governance.mock_dao_audit_replay import fingerprint_audit_ledger  # noqa: E402


def _load_json_object(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("expected JSON object")
    return data


def _load_ledger_array(path: Path) -> list[dict[str, object]]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("expected JSON array of audit rows")
    return list(data)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fingerprint lan_governance_replay_sidecar_v1 JSON or compare two files",
    )
    ap.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Sidecar JSON object (schema lan_governance_replay_sidecar_v1)",
    )
    ap.add_argument(
        "--compare",
        type=Path,
        metavar="FILE2",
        help="Second sidecar; exit 0 if fingerprints match",
    )
    ap.add_argument(
        "--audit-ledger",
        type=Path,
        metavar="AUDIT.json",
        help="MockDAO audit array JSON; must match sidecar audit_ledger_fingerprint when present",
    )
    args = ap.parse_args()

    if args.file is None:
        ap.print_help()
        return 2

    s1 = _load_json_object(args.file)
    schema = str(s1.get("schema") or "")
    if schema != LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1:
        print(
            f"warning: schema is {schema!r}, expected {LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1}",
            file=sys.stderr,
        )

    if args.audit_ledger is not None:
        afp = fingerprint_audit_ledger(_load_ledger_array(args.audit_ledger))
        embedded = s1.get("audit_ledger_fingerprint")
        if embedded is None:
            print(
                "error: sidecar has no audit_ledger_fingerprint but --audit-ledger was set",
                file=sys.stderr,
            )
            return 1
        if str(embedded) != afp:
            print(f"audit mismatch sidecar={embedded} ledger_file={afp}", file=sys.stderr)
            return 1

    fp1 = fingerprint_replay_sidecar(s1)
    if args.compare is None:
        print(fp1)
        return 0

    s2 = _load_json_object(args.compare)
    fp2 = fingerprint_replay_sidecar(s2)
    if fp1 == fp2:
        print(f"match fingerprint={fp1}")
        return 0
    print(f"mismatch fp1={fp1}", file=sys.stderr)
    print(f"mismatch fp2={fp2}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
