"""
Prometheus metrics (opt-in via ``KERNEL_METRICS=1``).

Counters and histograms are no-ops when disabled or if ``prometheus_client`` is missing.
"""

from __future__ import annotations

import os
from typing import Any

_llm_histogram: Any = None
_chat_histogram: Any = None
_chat_paths: Any = None
_malabs_blocks: Any = None
_semantic_malabs_outcomes: Any = None
_dao_ops: Any = None
_embedding_errors: Any = None
_kernel_decisions: Any = None
_kernel_process_seconds: Any = None
_initialized = False


def metrics_enabled() -> bool:
    return os.environ.get("KERNEL_METRICS", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def init_metrics() -> None:
    """Register Prometheus metrics once (safe to call multiple times)."""
    global _initialized, _llm_histogram, _chat_histogram, _chat_paths
    global _malabs_blocks, _semantic_malabs_outcomes, _dao_ops, _embedding_errors
    global _kernel_decisions, _kernel_process_seconds

    if _initialized:
        return
    _initialized = True

    if not metrics_enabled():
        return

    try:
        from prometheus_client import Counter, Histogram
    except ImportError:
        return

    _llm_histogram = Histogram(
        "ethos_kernel_llm_completion_seconds",
        "Wall time for LLM completion calls (perceive / communicate / narrate).",
        ["operation"],
        buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 120.0, float("inf")),
    )
    _chat_histogram = Histogram(
        "ethos_kernel_chat_turn_duration_seconds",
        "End-to-end synchronous chat turn duration inside the worker thread.",
        ["path"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, float("inf")),
    )
    _chat_paths = Counter(
        "ethos_kernel_chat_turns_total",
        "Chat turns completed by result path.",
        ["path"],
    )
    _malabs_blocks = Counter(
        "ethos_kernel_malabs_blocks_total",
        "Safety / MalAbs-related blocks (by coarse path).",
        ["reason"],
    )
    _semantic_malabs_outcomes = Counter(
        "ethos_kernel_semantic_malabs_outcomes_total",
        "Semantic MalAbs tier outcomes after lexical pass (see semantic_chat_gate.py).",
        ["outcome"],
    )
    _dao_ops = Counter(
        "ethos_kernel_dao_ws_operations_total",
        "DAO WebSocket operations (mock governance).",
        ["operation"],
    )
    _embedding_errors = Counter(
        "ethos_kernel_embedding_errors_total",
        "Semantic MalAbs embedding tier failures (HTTP or backend).",
        ["source"],
    )
    # Bounded label cardinality: action is a coarse slug (see record_kernel_decision_metrics).
    _kernel_decisions = Counter(
        "ethos_kernel_kernel_decisions_total",
        "EthicalKernel.process outcomes (one per completed decision).",
        ["action", "certainty", "blocked"],
    )
    _kernel_process_seconds = Histogram(
        "ethos_kernel_kernel_process_seconds",
        "Wall time for EthicalKernel.process (full ethical cycle).",
        buckets=(0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, float("inf")),
    )


def observe_llm_completion_seconds(operation: str, seconds: float) -> None:
    if _llm_histogram is None:
        return
    _llm_histogram.labels(operation=operation).observe(max(0.0, seconds))


def observe_chat_turn(path: str, duration_s: float) -> None:
    if _chat_histogram is None or _chat_paths is None:
        return
    p = path if path else "unknown"
    _chat_histogram.labels(path=p).observe(max(0.0, duration_s))
    _chat_paths.labels(path=p).inc()


def record_malabs_block(reason: str) -> None:
    if _malabs_blocks is None:
        return
    _malabs_blocks.labels(reason=reason).inc()


def record_semantic_malabs_outcome(outcome: str) -> None:
    """Count one semantic-tier decision (embedding / arbiter paths)."""
    if _semantic_malabs_outcomes is None:
        return
    o = (outcome or "unknown").strip()[:64] or "unknown"
    _semantic_malabs_outcomes.labels(outcome=o).inc()


def record_dao_ws_operation(operation: str) -> None:
    if _dao_ops is None:
        return
    _dao_ops.labels(operation=operation).inc()


def observe_embedding_error(source: str) -> None:
    if _embedding_errors is None:
        return
    _embedding_errors.labels(source=source).inc()


def _action_label_for_metrics(final_action: str, *, blocked: bool) -> str:
    """Coarse action slug to limit Prometheus label cardinality."""
    if blocked:
        return "blocked"
    raw = (final_action or "").strip()[:48]
    if not raw:
        return "unknown"
    return "".join(c if c.isalnum() or c in "_" else "_" for c in raw)[:40] or "unknown"


def _certainty_label(d: Any) -> str:
    """Map Bayesian uncertainty to a small enum (avoid high-cardinality floats)."""
    if getattr(d, "blocked", False) or getattr(d, "bayesian_result", None) is None:
        return "n_a"
    u = float(d.bayesian_result.uncertainty)
    if u < 0.25:
        return "high"
    if u < 0.5:
        return "med"
    return "low"


def record_kernel_decision_metrics(d: Any) -> None:
    """
    Record one ``EthicalKernel.process`` completion.

    ``d`` is a **KernelDecision**; imported lazily to avoid circular imports.
    Labels: ``action`` (coarse slug), ``certainty`` (high/med/low/n_a), ``blocked`` (true/false).
    """
    if _kernel_decisions is None:
        return
    blocked = bool(getattr(d, "blocked", False))
    action = _action_label_for_metrics(str(getattr(d, "final_action", "")), blocked=blocked)
    cert = _certainty_label(d)
    blk = "true" if blocked else "false"
    _kernel_decisions.labels(action=action, certainty=cert, blocked=blk).inc()


def observe_kernel_process_seconds(seconds: float) -> None:
    if _kernel_process_seconds is None:
        return
    _kernel_process_seconds.observe(max(0.0, seconds))
