"""
Ethos Kernel **runtime** entrypoints: long-lived process wiring.

The ethical policy remains exclusively in ``EthicalKernel`` (``src.kernel``).
This package only exposes how the ASGI server and optional read-only helpers start.

``get_uvicorn_bind`` / ``run_chat_server`` are imported lazily so ``chat_server`` can
depend on ``runtime.telemetry`` without a circular import.

See docs/proposals/RUNTIME_CONTRACT.md and docs/proposals/RUNTIME_PHASES.md.
"""

from __future__ import annotations

from typing import Tuple

from .telemetry import (
    advisory_interval_seconds_from_env,
    advisory_loop,
    advisory_snapshot,
)

__all__ = [
    "get_uvicorn_bind",
    "run_chat_server",
    "advisory_interval_seconds_from_env",
    "advisory_loop",
    "advisory_snapshot",
]


def get_uvicorn_bind() -> Tuple[str, int]:
    from ..chat_server import get_uvicorn_bind as _impl

    return _impl()


def run_chat_server() -> None:
    from ..chat_server import run_chat_server as _impl

    _impl()
