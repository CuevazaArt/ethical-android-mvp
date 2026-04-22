"""argparse contract for `scripts/eval/run_burst_cancel_smoke.py` (fail-fast before thread pool)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "eval" / "run_burst_cancel_smoke.py"


def _run_cli(args: list[str], *, timeout_s: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )


def test_run_burst_script_argparse_rejects_nonfinite_delay() -> None:
    p = _run_cli(["--delay", "nan", "--workers", "1"])
    assert p.returncode == 2, (p.stderr, p.stdout)


def test_run_burst_script_argparse_rejects_inf_join_timeout() -> None:
    p = _run_cli(["--join-timeout", "inf", "--workers", "1"])
    assert p.returncode == 2, (p.stderr, p.stdout)


def test_run_burst_script_argparse_rejects_workers_out_of_range() -> None:
    p = _run_cli(["--workers", "0"])
    assert p.returncode == 2, (p.stderr, p.stdout)


def test_run_burst_script_argparse_rejects_negative_cancel_after() -> None:
    p = _run_cli(["--cancel-after", "-0.1", "--workers", "1"])
    assert p.returncode == 2, (p.stderr, p.stdout)
