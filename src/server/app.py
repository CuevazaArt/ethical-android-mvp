"""
FastAPI **app** re-export (Bloque 34.5, incremental).

The live :class:`fastapi.FastAPI` instance is still built in :mod:`src.chat_server`
(import-time profile merge, env validation, mount order, monolith WebSocket).
This module is a **stable** ASGI import path: ``uvicorn src.server.app:app``.

Do not duplicate construction here — import order must remain single-sourced
until the remaining routes move out of ``chat_server.py``.
"""

from __future__ import annotations

from src.chat_server import app

__all__ = ["app"]
