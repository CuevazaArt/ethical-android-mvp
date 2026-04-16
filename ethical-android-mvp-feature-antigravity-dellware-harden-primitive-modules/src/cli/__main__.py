"""
CLI for operators: config validation, profile partition checks.

Example::

    python -m src.cli check-config
    python -m src.cli check-config --strict
"""

from __future__ import annotations

import argparse
import sys

from src.validators.env_policy import (
    collect_env_violations,
    validate_kernel_env,
    validate_supported_combo_partition,
)


def _cmd_check_config(*, strict: bool) -> int:
    validate_supported_combo_partition()
    if strict:
        validate_kernel_env(mode="strict")
        print("check-config: OK (strict: no KERNEL_* consistency violations).")
        return 0
    violations = collect_env_violations()
    if violations:
        print("check-config: warnings (set --strict to fail):")
        for v in violations:
            print(f"  - {v}")
        return 0
    print("check-config: OK (no consistency violations).")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m src.cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser(
        "check-config",
        help="Validate ETHOS_RUNTIME_PROFILE name and KERNEL_* cross-flag rules.",
    )
    c.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any rule in collect_env_violations() fails.",
    )

    args = p.parse_args(argv)
    if args.cmd == "check-config":
        try:
            return _cmd_check_config(strict=args.strict)
        except (AssertionError, ValueError) as e:
            print(f"check-config: FAILED\n{e}", file=sys.stderr)
            return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
