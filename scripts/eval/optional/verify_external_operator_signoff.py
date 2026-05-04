"""V2.131: verify the MVP external operator signoff is real.

A `MVP_CLOSURE_REPORT` declared "deliverable" by the same agent that
wrote the code is, by definition, self-attestation. Before any
`v1.0-mvp-text-mediated` tag is cut, a non-author operator must run the
runbook end-to-end on a clean checkout and record the result in
`docs/collaboration/evidence/MVP_EXTERNAL_OPERATOR_SIGNOFF.json`.

This script enforces the minimum schema for that signoff:

* `verified` must be boolean True.
* `operator` must be a non-empty string and must NOT match any author
  identity listed in `--author` (defaults to the obvious local-author
  markers, which the caller can extend).
* `verified_at` must be an RFC-3339 UTC timestamp.
* `evidence_run_id` must match the `run_id` field inside the latest
  `OPERATOR_INTERACTION_DEMO.json`. This binds the signoff to a real
  run instead of a free-text claim.

Exit code is non-zero when any rule fails. CI / release automation can
gate on it. The script is intentionally read-only: it never mutates the
signoff file (so an agent cannot quietly approve itself).

Usage::

    python scripts/eval/verify_external_operator_signoff.py
    python scripts/eval/verify_external_operator_signoff.py \\
        --signoff docs/collaboration/evidence/MVP_EXTERNAL_OPERATOR_SIGNOFF.json \\
        --demo docs/collaboration/evidence/OPERATOR_INTERACTION_DEMO.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SIGNOFF = (
    ROOT / "docs" / "collaboration" / "evidence" / "MVP_EXTERNAL_OPERATOR_SIGNOFF.json"
)
DEFAULT_DEMO = (
    ROOT / "docs" / "collaboration" / "evidence" / "OPERATOR_INTERACTION_DEMO.json"
)
# Author identities that must NEVER be accepted as the external operator.
# The list is intentionally conservative; --author lets the caller extend it.
DEFAULT_AUTHOR_IDENTITIES: tuple[str, ...] = (
    "automation-runner",
    "agent",
    "copilot",
    "self",
    "anonymous",
    "unknown",
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_iso_utc(raw: str) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def verify_signoff(
    *,
    signoff: dict[str, Any],
    demo: dict[str, Any] | None,
    author_identities: tuple[str, ...] = DEFAULT_AUTHOR_IDENTITIES,
) -> tuple[bool, list[str]]:
    """Return (ok, reasons). `ok` is True only if every rule passes."""

    reasons: list[str] = []

    if signoff.get("schema_version") != "1":
        reasons.append("schema_version must be '1'")

    if signoff.get("verified") is not True:
        reasons.append("verified must be true")

    operator = signoff.get("operator")
    if not isinstance(operator, str) or not operator.strip():
        reasons.append("operator must be a non-empty string")
    else:
        normalized = operator.strip().lower()
        deny_set = {a.lower() for a in author_identities}
        if normalized in deny_set:
            reasons.append(
                f"operator '{operator}' is in the author/automation deny-list; "
                "an external human is required"
            )

    verified_at = signoff.get("verified_at")
    if _parse_iso_utc(str(verified_at) if verified_at is not None else "") is None:
        reasons.append("verified_at must be an RFC-3339 UTC timestamp")

    evidence_run_id = signoff.get("evidence_run_id")
    if not isinstance(evidence_run_id, str) or not evidence_run_id.strip():
        reasons.append("evidence_run_id must be a non-empty string")
    elif demo is None:
        reasons.append("OPERATOR_INTERACTION_DEMO.json is missing; cannot bind signoff")
    else:
        demo_run_id = str(demo.get("run_id", "")).strip()
        if not demo_run_id:
            reasons.append("OPERATOR_INTERACTION_DEMO.json has no run_id to bind")
        elif demo_run_id != evidence_run_id.strip():
            reasons.append(
                "evidence_run_id does not match the latest OPERATOR_INTERACTION_DEMO "
                f"run_id (signoff={evidence_run_id!r}, demo={demo_run_id!r})"
            )
        elif demo.get("passed") is not True:
            reasons.append(
                "OPERATOR_INTERACTION_DEMO.json shows passed!=true; "
                "external operator cannot sign off on a failing run"
            )

    return (len(reasons) == 0, reasons)


def _verify_directory(
    *,
    signoff_dir: Path,
    demo: dict[str, Any] | None,
    author_identities: tuple[str, ...],
    min_signoffs: int,
) -> tuple[bool, list[dict[str, Any]]]:
    """Verify all *.json signoff files in *signoff_dir*.

    Returns (overall_ok, per_file_results).
    ``overall_ok`` is True when at least ``min_signoffs`` files pass.
    """
    candidates = sorted(signoff_dir.glob("*.json"))
    if not candidates:
        return False, [
            {
                "file": str(signoff_dir),
                "ok": False,
                "reasons": ["no .json files found in directory"],
            }
        ]

    per_file: list[dict[str, Any]] = []
    n_ok = 0
    for path in candidates:
        try:
            signoff = _load_json(path)
        except Exception as exc:
            per_file.append({"file": path.name, "ok": False, "reasons": [str(exc)]})
            continue
        ok, reasons = verify_signoff(
            signoff=signoff,
            demo=demo,
            author_identities=author_identities,
        )
        if ok:
            n_ok += 1
        try:
            file_display = path.resolve().relative_to(ROOT).as_posix()
        except (ValueError, OSError):
            file_display = path.name
        per_file.append({"file": file_display, "ok": ok, "reasons": reasons})

    overall_ok = n_ok >= min_signoffs
    return overall_ok, per_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the MVP external operator signoff is real and matches a "
            "passing OPERATOR_INTERACTION_DEMO run. "
            "Accepts a single signoff file (--signoff) or a directory of "
            "signoff files (--signoff-dir)."
        )
    )
    parser.add_argument("--signoff", type=Path, default=DEFAULT_SIGNOFF)
    parser.add_argument(
        "--signoff-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing one or more operator signoff JSON files. "
            "When provided, --signoff is ignored."
        ),
    )
    parser.add_argument("--demo", type=Path, default=DEFAULT_DEMO)
    parser.add_argument(
        "--min-signoffs",
        type=int,
        default=1,
        help="Minimum number of passing signoffs required (default: 1). Only used with --signoff-dir.",
    )
    parser.add_argument(
        "--author",
        action="append",
        default=None,
        help=(
            "Additional identity that must NOT be accepted as the external "
            "operator. May be passed multiple times."
        ),
    )
    args = parser.parse_args()

    try:
        demo = _load_json(args.demo)
    except FileNotFoundError:
        demo = None

    extra_authors = tuple(args.author or ())
    author_identities = DEFAULT_AUTHOR_IDENTITIES + extra_authors

    if args.signoff_dir is not None:
        if not args.signoff_dir.is_dir():
            print(
                json.dumps(
                    {"ok": False, "error": f"not a directory: {args.signoff_dir}"},
                    indent=2,
                )
            )
            return 2
        overall_ok, per_file = _verify_directory(
            signoff_dir=args.signoff_dir,
            demo=demo,
            author_identities=author_identities,
            min_signoffs=args.min_signoffs,
        )
        n_ok = sum(1 for f in per_file if f["ok"])
        print(
            json.dumps(
                {
                    "ok": overall_ok,
                    "signoff_dir": str(args.signoff_dir),
                    "n_files_checked": len(per_file),
                    "n_files_ok": n_ok,
                    "min_required": args.min_signoffs,
                    "per_file": per_file,
                },
                indent=2,
            )
        )
        return 0 if overall_ok else 1

    try:
        signoff = _load_json(args.signoff)
    except FileNotFoundError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    ok, reasons = verify_signoff(
        signoff=signoff,
        demo=demo,
        author_identities=author_identities,
    )
    try:
        signoff_display = args.signoff.resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        signoff_display = args.signoff.name
    print(
        json.dumps(
            {
                "ok": ok,
                "signoff": signoff_display,
                "reasons": reasons,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
