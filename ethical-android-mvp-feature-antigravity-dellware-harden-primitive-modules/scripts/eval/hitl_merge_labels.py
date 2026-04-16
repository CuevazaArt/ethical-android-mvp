#!/usr/bin/env python3
"""
Merge human labels into red-team JSONL for threshold tuning / offline review.

Input rows (JSONL) may contain model predictions; operators add::

    "human_blocked": true|false
    "human_notes": "optional string"

This script writes ``summary.json`` with disagreement counts next to the input file.

Usage::

    python scripts/eval/hitl_merge_labels.py --input scripts/eval/red_team_prompts.labeled.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    args = ap.parse_args()
    path: Path = args.input
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))

    disagreements = 0
    labeled = 0
    for r in rows:
        if "human_blocked" not in r:
            continue
        labeled += 1
        if bool(r.get("expect_blocked")) != bool(r["human_blocked"]):
            disagreements += 1

    out = {
        "source": str(path),
        "rows": len(rows),
        "human_labeled": labeled,
        "disagreements_with_expect_blocked": disagreements,
    }
    summary_path = path.with_suffix(path.suffix + ".summary.json")
    summary_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(summary_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
