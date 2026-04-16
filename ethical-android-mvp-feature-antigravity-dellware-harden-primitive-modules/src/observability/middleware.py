"""HTTP middleware: propagate ``X-Request-ID`` for structured logs."""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .context import set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Read or generate ``X-Request-ID``; echo on the response; set logging context."""

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get("x-request-id") or request.headers.get("X-Request-ID")
        rid = (incoming or "").strip() or str(uuid.uuid4())
        set_request_id(rid)
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
