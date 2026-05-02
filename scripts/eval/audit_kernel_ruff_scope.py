"""Run Ruff on `src` and `tests` (same scope as CI).

Vendored `llama_cpp` under the Nomad Android tree is excluded via `pyproject.toml`
(`tool.ruff.exclude`).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument(
        "extra_args",
        nargs="*",
        help="Additional arguments forwarded to ruff.",
    )
    args = parser.parse_args()

    root = _repo_root()
    cmd = [sys.executable, "-m", "ruff", "check", "src", "tests"]
    if args.extra_args:
        cmd.extend(args.extra_args)

    completed = subprocess.run(cmd, check=False, cwd=root)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
