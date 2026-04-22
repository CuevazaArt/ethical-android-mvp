#!/usr/bin/env python3
"""
Run red-team prompts against :class:`~src.modules.absolute_evil.AbsoluteEvilDetector`.

Metrics (English labels for logs):
  - ``true_block``: ``expect_blocked`` and ``blocked``
  - ``false_block``: not ``expect_blocked`` but ``blocked`` (over-block)
  - ``false_allow``: ``expect_blocked`` but not ``blocked`` (under-block)
  - ``true_allow``: not ``expect_blocked`` and not ``blocked``

Usage (from repo root)::

    python scripts/eval/run_red_team.py
    python scripts/eval/run_red_team.py --jsonl scripts/eval/red_team_prompts.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


@dataclass
class RedTeamRow:
    id: str
    text_en: str
    expect_blocked: bool
    category: str = ""
    notes: str = ""


def load_jsonl(path: Path) -> list[RedTeamRow]:
    rows: list[RedTeamRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        o: dict[str, Any] = json.loads(line)
        rows.append(
            RedTeamRow(
                id=str(o.get("id", "")),
                text_en=str(o.get("text_en", "")),
                expect_blocked=bool(o.get("expect_blocked")),
                category=str(o.get("category", "")),
                notes=str(o.get("notes", "")),
            )
        )
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description="MalAbs red-team batch runner")
    p.add_argument(
        "--jsonl",
        type=Path,
        default=Path(__file__).resolve().parent / "red_team_prompts.jsonl",
    )
    args = p.parse_args()

    from src.modules.ethics.absolute_evil import AbsoluteEvilDetector

    det = AbsoluteEvilDetector()
    rows = load_jsonl(args.jsonl)
    counts = {"true_block": 0, "false_block": 0, "false_allow": 0, "true_allow": 0}
    for r in rows:
        res = det.evaluate_chat_text(r.text_en, llm_backend=None)
        blocked = bool(res.blocked)
        exp = r.expect_blocked
        if exp and blocked:
            counts["true_block"] += 1
            tag = "true_block"
        elif exp and not blocked:
            counts["false_allow"] += 1
            tag = "false_allow"
        elif not exp and blocked:
            counts["false_block"] += 1
            tag = "false_block"
        else:
            counts["true_allow"] += 1
            tag = "true_allow"
        print(f"{r.id}\t{tag}\tblocked={blocked}\t{res.reason[:120]}")

    n = len(rows) or 1
    print("---")
    print(json.dumps({k: counts[k] for k in sorted(counts)}, indent=2))
    print(
        "rates",
        json.dumps(
            {
                "block_precision_on_expected_harm": counts["true_block"]
                / max(1, counts["true_block"] + counts["false_allow"]),
                "allow_rate_on_expected_safe": counts["true_allow"]
                / max(1, counts["true_allow"] + counts["false_block"]),
                "n": len(rows),
            },
            indent=2,
        ),
    )


if __name__ == "__main__":
    main()
