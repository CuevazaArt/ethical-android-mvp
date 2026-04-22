"""Process-level metadata shared by HTTP route modules (avoids circular imports with ``chat_server``)."""

from __future__ import annotations

import time

_PROCESS_START_MONOTONIC = time.monotonic()


def package_version() -> str:
    try:
        from importlib.metadata import version

        return version("ethos-kernel")
    except Exception:
        return "dev"


def uptime_seconds_rounded() -> float:
    return round(time.monotonic() - _PROCESS_START_MONOTONIC, 3)
