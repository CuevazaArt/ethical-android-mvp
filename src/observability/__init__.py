"""Runtime observability: Prometheus metrics, structured logging, request correlation."""

from .context import clear_request_context, request_id_var, set_request_id
from .logging_setup import configure_logging
from .metrics import (
    init_metrics,
    metrics_enabled,
    observe_chat_turn,
    observe_embedding_error,
    observe_llm_completion_seconds,
    record_dao_ws_operation,
    record_malabs_block,
)

__all__ = [
    "clear_request_context",
    "configure_logging",
    "init_metrics",
    "metrics_enabled",
    "observe_chat_turn",
    "observe_embedding_error",
    "observe_llm_completion_seconds",
    "record_dao_ws_operation",
    "record_malabs_block",
    "request_id_var",
    "set_request_id",
]
