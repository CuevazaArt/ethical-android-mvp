"""Structured logging: optional JSON lines and ``request_id`` on records."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from .context import request_id_var

_logging_configured = False


class _JsonFormatter(logging.Formatter):
    """One JSON object per line; includes ``request_id`` when set in context."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = request_id_var.get()
        if rid:
            payload["request_id"] = rid
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """
    Configure root handler once: JSON to stderr if ``KERNEL_LOG_JSON=1``, else plain text.

    Level from ``KERNEL_LOG_LEVEL`` (default ``INFO``).
    """
    global _logging_configured
    if _logging_configured:
        return
    level_name = os.environ.get("KERNEL_LOG_LEVEL", "INFO").strip().upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    if os.environ.get("KERNEL_LOG_JSON", "").strip().lower() in ("1", "true", "yes", "on"):
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root.addHandler(handler)
    _logging_configured = True
