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
_perception_circuit_trips: Any = None
_chat_async_timeouts: Any = None
_llm_cancel_scope_signals: Any = None
_chat_abandoned_effects_skipped: Any = None
_lan_envelope_replay_cache_events: Any = None
_limbic_tension: Any = None
_ttft_histogram: Any = None
_nomad_connections: Any = None
_nomad_bridge_rejections: Any = None
_nomad_bridge_queue_evictions: Any = None
_initialized = False

_LAN_ENVELOPE_REPLAY_CACHE_EVENTS = frozenset({"hit", "miss", "evict_ttl", "evict_lru"})
_NOMAD_REJECTION_REASONS = frozenset(
    {
        "ws_oversize",
        "invalid_json",
        "invalid_envelope",
        "vision_reject",
        "audio_reject",
        "telemetry_reject",
    }
)
_NOMAD_EVICTION_QUEUES = frozenset({"vision", "audio", "telemetry"})


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
    global _kernel_decisions, _kernel_process_seconds, _perception_circuit_trips
    global _chat_async_timeouts, _llm_cancel_scope_signals, _chat_abandoned_effects_skipped
    global _lan_envelope_replay_cache_events, _limbic_tension, _ttft_histogram, _nomad_connections
    global _nomad_bridge_rejections, _nomad_bridge_queue_evictions

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
    _chat_async_timeouts = Counter(
        "ethos_kernel_chat_turn_async_timeouts_total",
        "Async wait for chat turn exceeded KERNEL_CHAT_TURN_TIMEOUT (sync LLM may still run).",
    )
    _llm_cancel_scope_signals = Counter(
        "ethos_kernel_llm_cancel_scope_signals_total",
        "Chat async deadline set the cooperative cancel event (worker may still finish in-flight HTTP).",
    )
    _chat_abandoned_effects_skipped = Counter(
        "ethos_kernel_chat_turn_abandoned_effects_skipped_total",
        "Late chat worker completion skipped STM/post-turn effects after KERNEL_CHAT_TURN_TIMEOUT.",
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
    _perception_circuit_trips = Counter(
        "ethos_kernel_perception_circuit_trips_total",
        "Times perception validation streak exceeded threshold (metacognitive doubt).",
    )
    _lan_envelope_replay_cache_events = Counter(
        "ethos_kernel_lan_envelope_replay_cache_events_total",
        "LAN governance envelope replay-cache events (hits, misses, evictions).",
        ["event"],
    )
    _kernel_process_seconds = Histogram(
        "ethos_kernel_kernel_process_seconds",
        "Wall time for EthicalKernel.process (full ethical cycle).",
        buckets=(
            0.0005,
            0.001,
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            float("inf"),
        ),
    )
    _nomad_bridge_rejections = Counter(
        "ethos_kernel_nomad_bridge_rejections_total",
        "Nomad LAN WebSocket ingest rejections (see nomad_bridge.public_queue_stats rejections).",
        ["reason"],
    )
    _nomad_bridge_queue_evictions = Counter(
        "ethos_kernel_nomad_bridge_queue_evictions_total",
        "Nomad bridge dropped oldest item because the bounded queue was full.",
        ["queue"],
    )
    _nomad_connections = Counter(
        "ethos_kernel_nomad_bridge_connections_total",
        "Total connections to the Nomad SmartPhone Bridge (S.2.1).",
        ["status"],
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


def record_chat_turn_async_timeout() -> None:
    """Count one WebSocket turn where ``asyncio.wait_for`` hit ``KERNEL_CHAT_TURN_TIMEOUT``."""
    if _chat_async_timeouts is None:
        return
    _chat_async_timeouts.inc()


def record_llm_cancel_scope_signaled() -> None:
    """Count when the cooperative LLM cancel event is set (paired with async timeout)."""
    if _llm_cancel_scope_signals is None:
        return
    _llm_cancel_scope_signals.inc()


def record_chat_turn_abandoned_effects_skipped() -> None:
    """Count when a late chat turn completion dropped STM side effects (see ``abandon_chat_turn``)."""
    if _chat_abandoned_effects_skipped is None:
        return
    _chat_abandoned_effects_skipped.inc()


def record_perception_circuit_trip() -> None:
    if _perception_circuit_trips is None:
        return
    _perception_circuit_trips.inc()


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


def record_nomad_bridge_rejection(reason: str) -> None:
    """Count one rejected Nomad ingest event (bounded ``reason`` label)."""
    if _nomad_bridge_rejections is None:
        return
    r = (reason or "").strip()
    if r not in _NOMAD_REJECTION_REASONS:
        return
    _nomad_bridge_rejections.labels(reason=r).inc()


def record_nomad_bridge_queue_eviction(queue: str) -> None:
    """Count one queue eviction when a full Nomad buffer dropped the oldest item."""
    if _nomad_bridge_queue_evictions is None:
        return
    q = (queue or "").strip()
    if q not in _NOMAD_EVICTION_QUEUES:
        return
    _nomad_bridge_queue_evictions.labels(queue=q).inc()


def record_lan_envelope_replay_cache_event(event: str, *, amount: float = 1.0) -> None:
    """
    Count replay-cache activity for ``lan_governance_envelope`` (per-process aggregate).

    ``event`` must be one of: ``hit``, ``miss``, ``evict_ttl``, ``evict_lru`` (bounded cardinality).
    """
    if _lan_envelope_replay_cache_events is None:
        return
    e = (event or "").strip()
    if e not in _LAN_ENVELOPE_REPLAY_CACHE_EVENTS:
        return
    n = float(amount)
    if n <= 0:
        return
    _lan_envelope_replay_cache_events.labels(event=e).inc(n)


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


def set_limbic_tension(value: float) -> None:
    if _limbic_tension is None:
        return
    _limbic_tension.set(max(0.0, min(1.0, value)))


def observe_ttft_seconds(seconds: float) -> None:
    if _ttft_histogram is None:
        return
    _ttft_histogram.observe(max(0.0, seconds))


def record_nomad_bridge_connection(status: str = "connected") -> None:
    if _nomad_connections is None:
        return
    s = (status or "connected").strip()
    _nomad_connections.labels(status=s).inc()


def record_nomad_bridge_disconnection(status: str = "disconnected") -> None:
    if _nomad_connections is None:
        return
    s = (status or "disconnected").strip()
    _nomad_connections.labels(status=s).inc()
