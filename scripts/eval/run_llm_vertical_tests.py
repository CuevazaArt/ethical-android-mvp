"""Run focused LLM vertical regression tests (see PROPOSAL_LLM_VERTICAL_ROADMAP.md)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Keep in sync with docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md phase 5.
TEST_TARGETS = [
    "tests/test_llm_verbal_backend_policy.py",
    "tests/test_llm_touchpoint_policies.py",
    "tests/test_process_natural_verbal_observability.py",
    "tests/test_perception_dual_vote_failure.py",
    "tests/test_semantic_chat_gate.py",
    "tests/test_malabs_semantic_integration.py",
    "tests/test_generative_candidates.py",
    "tests/test_kernel_env_operator.py",
    "tests/test_observability_metrics.py",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="LLM vertical regression tests")
    ap.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Pass -q to pytest",
    )
    args = ap.parse_args()
    cmd = [sys.executable, "-m", "pytest", *TEST_TARGETS]
    if args.quiet:
        cmd.append("-q")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
