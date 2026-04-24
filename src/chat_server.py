"""
Ethos Kernel Entry Point (V2).

This module serves as the primary entry point for the uvicorn server,
delegating app construction to :mod:`src.server.app`.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Fix PYTHONPATH for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.server.app import app

logger = logging.getLogger(__name__)


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment."""
    host = os.environ.get("ETHOS_CHAT_HOST", "127.0.0.1")
    port = int(os.environ.get("ETHOS_CHAT_PORT", "8000"))
    return host, port


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

