"""
Ethos Kernel Entry Point (Lean Fachada).

This module serves as the primary entry point for the uvicorn server,
delegating app construction to :mod:`src.server.app`.
"""

from __future__ import annotations

import logging

from src.server.app import app

# Re-exports for tests and legacy callers
from src.server.ws_chat import _chat_turn_to_jsonable  # noqa: F401

logger = logging.getLogger(__name__)


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment; see :mod:`src.settings`."""
    from .settings import kernel_settings

    s = kernel_settings()
    return s.chat_host, s.chat_port


def run_chat_server() -> None:
    """Start uvicorn with the app (blocking)."""
    import uvicorn

    host, port = get_uvicorn_bind()
    # Note: we pass the app object directly, or the import string "src.server.app:app"
    uvicorn.run(app, host=host, port=port, reload=False)


def main() -> None:
    run_chat_server()


if __name__ == "__main__":
    main()
