"""Request / session correlation for logs (HTTP and WebSocket)."""

from __future__ import annotations

import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(rid: str | None = None) -> str:
    """Set (or generate) the current ``request_id``; return the value applied."""
    value = rid or str(uuid.uuid4())
    request_id_var.set(value)
    return value


def clear_request_context() -> None:
    """Reset correlation id (e.g. after WebSocket message handling)."""
    request_id_var.set(None)
