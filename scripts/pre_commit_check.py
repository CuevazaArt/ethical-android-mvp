#!/usr/bin/env python3
"""Pre-commit hook: fast local checks before push.

Install: copy to .git/hooks/pre-commit and chmod +x
Or: pip install pre-commit && pre-commit install
"""
import subprocess
import sys


def run(cmd: str, label: str) -> bool:
    """Run a check command and return True if it passes."""
    print(f"  [RUN] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [FAIL] {label} FAILED")
        if result.stdout:
            # Show first 20 lines of output to avoid flooding
            lines = result.stdout.strip().split("\n")[:20]
            print("\n".join(f"    {l}" for l in lines))
        return False
    print(f"  [OK] {label} OK")
    return True


def main() -> int:
    print("[INFO] Pre-commit checks...")
    checks = [
        ("python -m ruff check src tests --quiet", "Ruff lint"),
        ("python -m ruff format --check src tests --quiet", "Ruff format"),
        ("python -m mypy src --no-error-summary", "Mypy types"),
    ]
    passed = all(run(cmd, label) for cmd, label in checks)
    if not passed:
        print("\n[FAIL] Fix the above before committing.")
        return 1
    print("\n[OK] All pre-commit checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
