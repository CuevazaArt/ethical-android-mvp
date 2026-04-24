"""
Ethos Kernel — CLI (V2 Core)

Interfaz de línea de comandos para diagnósticos, checkpoints y exportación nomádica.

Usage::

    python -m src.ethos_cli diagnostics
    python -m src.ethos_cli config [--json] [--profiles] [--strict]

After ``pip install -e .``, the ``ethos`` console script is available.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _engine() -> Any:
    """Build a ChatEngine for CLI diagnostics."""
    from src.core.chat import ChatEngine
    return ChatEngine()


def cmd_diagnostics(args: argparse.Namespace) -> int:
    """Print kernel stats from V2 core."""
    engine = _engine()
    mem = engine.memory
    reflection = mem.reflection()
    payload = {
        "episodes": len(mem),
        "memory_reflection": reflection,
        "v2_core": True,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Ethos Kernel V2 — diagnostics")
        print(f"  Episodes in memory : {payload['episodes']}")
        print(f"  Reflection         : {reflection}")
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Show active environment config."""
    import os

    if args.profiles:
        print("No runtime profiles configured (V2 Core Minimal).")
        return 0

    report = {
        "OLLAMA_MODEL": os.environ.get("OLLAMA_MODEL", "llama3.2:1b"),
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "ETHOS_RUNTIME_PROFILE": os.environ.get("ETHOS_RUNTIME_PROFILE", "(none)"),
        "KERNEL_ENV_VALIDATION": os.environ.get("KERNEL_ENV_VALIDATION", "strict"),
        "v2_core": True,
    }
    exit_code = 0

    if args.strict:
        model = report["OLLAMA_MODEL"]
        if not model:
            report["strict_validation"] = {"ok": False, "error": "OLLAMA_MODEL is empty"}
            exit_code = 1
        else:
            report["strict_validation"] = {"ok": True}

    if args.json:
        print(json.dumps(report, indent=2))
        return exit_code

    print("Ethos Kernel V2 — configuration")
    for k, v in report.items():
        print(f"  {k}: {v}")
    return exit_code



def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ethos",
        description="Ethos Kernel CLI V2 (diagnostics, config).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_diag = sub.add_parser("diagnostics", help="Print kernel stats (V2 Core).")
    p_diag.add_argument("--json", action="store_true", help="Machine-readable JSON output.")
    p_diag.set_defaults(func=cmd_diagnostics)

    p_cfg = sub.add_parser("config", help="Environment config report.")
    p_cfg.add_argument("--json", action="store_true", help="Machine-readable output.")
    p_cfg.add_argument("--profiles", action="store_true", help="List runtime profile names.")
    p_cfg.add_argument("--strict", action="store_true", help="Validate env strictly; exit 1 on violations.")
    p_cfg.set_defaults(func=cmd_config)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = _build_parser()
    args = parser.parse_args(argv)
    fn = getattr(args, "func", None)
    if fn is None:
        parser.print_help()
        return 2
    return int(fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
