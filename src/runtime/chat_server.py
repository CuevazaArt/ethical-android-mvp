"""
ASGI application surface for operator and tooling (Bloque 32.1).

Stable bind target::

    uvicorn src.runtime.chat_server:app --host 127.0.0.1 --port 8765

The FastAPI application and HTTP/WebSocket route graph remain implemented in
:mod:`src.chat_server` until the monolith is split without orphan symbols.
This module re-exports ``app`` (and lifecycle helpers) so ``uvicorn src.runtime.chat_server:app`` and
``uvicorn src.chat_server:app`` resolve to the **same** application object (see
``tests/test_runtime_chat_server.py``).

``lifespan`` is defined once in :mod:`src.runtime.chat_lifecycle` and wired on the
FastAPI constructor in ``src.chat_server`` — do not duplicate startup/shutdown there.

This module re-exports ``chat_lifespan`` (and ``api_docs_enabled``) so operators and
tests can import a single stable surface: ``from src.runtime.chat_server import app,
chat_lifespan``.

Importing this module runs the same import-time guards as ``src.chat_server``
(profile merge and env validation).
"""

from __future__ import annotations

from ..chat_server import app
from .chat_lifecycle import api_docs_enabled, chat_lifespan

__all__ = ["api_docs_enabled", "app", "chat_lifespan"]
