"""Runtime observability: Prometheus metrics, structured logging, request correlation."""

from .context import clear_request_context, request_id_var, set_request_id
from .decision_log import decision_log_enabled, log_kernel_decision_event
from .logging_setup import configure_logging
from .metrics import (
    init_metrics,
    metrics_enabled,
    observe_chat_turn,
    observe_embedding_error,
    observe_kernel_process_seconds,
    observe_llm_completion_seconds,
    record_dao_ws_operation,
    record_kernel_decision_metrics,
    record_malabs_block,
)

__all__ = [
    "clear_request_context",
    "configure_logging",
    "decision_log_enabled",
    "init_metrics",
    "log_kernel_decision_event",
    "metrics_enabled",
    "observe_chat_turn",
    "observe_embedding_error",
    "observe_kernel_process_seconds",
    "observe_llm_completion_seconds",
    "record_dao_ws_operation",
    "record_kernel_decision_metrics",
    "record_malabs_block",
    "request_id_var",
    "set_request_id",
]
