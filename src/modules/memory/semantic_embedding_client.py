"""
HTTP embedding transport for semantic MalAbs (Ollama ``/api/embeddings``).

Features: configurable timeout/retries/backoff, circuit breaker, latency/failure counters,
and optional **hash-scoped** unit vectors when the service is down (opt-in; not semantic similarity).

Env:

- ``KERNEL_SEMANTIC_EMBED_TIMEOUT_S`` — per-request timeout (default ``12``).
- ``KERNEL_SEMANTIC_EMBED_RETRIES`` — extra attempts after first failure (default ``2``).
- ``KERNEL_SEMANTIC_EMBED_BACKOFF_S`` — base sleep between retries (default ``0.25``).
- ``KERNEL_SEMANTIC_EMBED_CIRCUIT_FAILURES`` — consecutive failures before opening circuit (default ``5``).
- ``KERNEL_SEMANTIC_EMBED_CIRCUIT_COOLDOWN_S`` — seconds circuit stays open (default ``45``).
- ``KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`` — ``1`` to emit deterministic hash vectors when HTTP/circuit fails (default **on** when unset; set ``0`` to disable).
- ``KERNEL_SEMANTIC_EMBED_HASH_DIM`` — dimension for hash fallback (default ``256``).
- ``KERNEL_SEMANTIC_EMBED_HASH_SCOPE`` — ASCII scope string mixed into hash (default ``malabs_embed_v1``).
"""
# Status: SCAFFOLD

from __future__ import annotations

import asyncio
import hashlib
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
import numpy as np


@dataclass
class EmbeddingTransportStats:
    """Thread-safe counters for operators and tests (not high-precision telemetry)."""

    last_latency_ms: float = 0.0
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    consecutive_failures: int = 0
    circuit_open_until_monotonic: float = 0.0
    last_error_short: str = ""
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def to_public_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "last_latency_ms": self.last_latency_ms,
                "total_requests": self.total_requests,
                "total_successes": self.total_successes,
                "total_failures": self.total_failures,
                "consecutive_failures": self.consecutive_failures,
                "circuit_open_until_monotonic": self.circuit_open_until_monotonic,
                "last_error_short": self.last_error_short,
            }


_stats = EmbeddingTransportStats()


def get_embedding_transport_stats() -> dict[str, Any]:
    """Snapshot of transport metrics (safe for JSON logging)."""
    return _stats.to_public_dict()


def reset_embedding_transport_stats_for_tests() -> None:
    """Reset counters (pytest only)."""
    with _stats._lock:
        _stats.last_latency_ms = 0.0
        _stats.total_requests = 0
        _stats.total_successes = 0
        _stats.total_failures = 0
        _stats.consecutive_failures = 0
        _stats.circuit_open_until_monotonic = 0.0
        _stats.last_error_short = ""


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _circuit_thresholds() -> tuple[int, float]:
    return (
        max(1, _env_int("KERNEL_SEMANTIC_EMBED_CIRCUIT_FAILURES", 5)),
        max(1.0, _env_float("KERNEL_SEMANTIC_EMBED_CIRCUIT_COOLDOWN_S", 45.0)),
    )


def _record_success(latency_ms: float) -> None:
    with _stats._lock:
        _stats.last_latency_ms = latency_ms
        _stats.total_requests += 1
        _stats.total_successes += 1
        _stats.consecutive_failures = 0


def _record_failure(msg: str) -> None:
    now = time.monotonic()
    with _stats._lock:
        _stats.total_requests += 1
        _stats.total_failures += 1
        _stats.consecutive_failures += 1
        short = (msg or "")[:200]
        _stats.last_error_short = short
        thr, cool = _circuit_thresholds()
        if _stats.consecutive_failures >= thr:
            _stats.circuit_open_until_monotonic = now + cool


def _circuit_blocks() -> bool:
    return time.monotonic() < _stats.circuit_open_until_monotonic


def hash_scoped_unit_embedding(
    text: str,
    *,
    dim: int | None = None,
    scope: str | None = None,
) -> np.ndarray | None:
    """
    Deterministic unit vector from ``text`` (not a neural embedding).

    Same phrase → same vector; different scope strings → different vectors. Use only when
    HTTP embeddings are unavailable and ``KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=1``.
    """
    d = dim if dim is not None else max(32, _env_int("KERNEL_SEMANTIC_EMBED_HASH_DIM", 256))
    sc = str(
        scope or os.environ.get("KERNEL_SEMANTIC_EMBED_HASH_SCOPE") or "malabs_embed_v1"
    ).encode("utf-8", errors="replace")
    payload = sc + b"|" + (text or "").encode("utf-8", errors="replace")
    out = np.zeros(d, dtype=np.float64)
    seed = hashlib.sha256(payload).digest()
    for i in range(d):
        seed = hashlib.sha256(seed + i.to_bytes(4, "big")).digest()
        out[i] = int.from_bytes(seed[:8], "big", signed=False) / float(2**64) * 2.0 - 1.0
    n = float(np.linalg.norm(out))
    if n < 1e-12:
        return None
    return out / n


def http_fetch_ollama_embedding(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
) -> np.ndarray | None:
    """
    POST Ollama embeddings JSON; return unit L2 vector or ``None``.
    """
    return http_fetch_ollama_embedding_with_policy(url, model, prompt, timeout_s=timeout_s)


_aclient: httpx.AsyncClient | None = None
_aclient_lock = asyncio.Lock()


async def _get_aclient() -> httpx.AsyncClient:
    """Singleton pattern for managing a persistent AsyncClient."""
    global _aclient
    if _aclient is None or _aclient.is_closed:
        async with _aclient_lock:
            if _aclient is None or _aclient.is_closed:
                import httpx

                _aclient = httpx.AsyncClient(
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                    timeout=httpx.Timeout(20.0),
                )
    return _aclient


async def ahttp_fetch_ollama_embedding(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
    aclient: httpx.AsyncClient | None = None,
) -> np.ndarray | None:
    """
    Async POST Ollama embeddings JSON; return unit L2 vector or ``None``.
    """
    return await ahttp_fetch_ollama_embedding_with_policy(
        url, model, prompt, timeout_s=timeout_s, aclient=aclient
    )


def _post_once(client: Any, url: str, payload: dict[str, Any]) -> list[float] | None:
    r = client.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    # New API: 'embeddings' is a list of lists; Legacy: 'embedding' is a flat list
    emb = data.get("embedding")
    if not emb and "embeddings" in data:
        embs = data["embeddings"]
        if isinstance(embs, list) and len(embs) > 0:
            emb = embs[0]
    if not emb or not isinstance(emb, list):
        return None
    arr = np.asarray([float(x) for x in emb], dtype=np.float64).reshape(-1)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        return None
    n = float(np.linalg.norm(arr))
    if n < 1e-12:
        return None
    return (arr / n).tolist()


async def _apost_once(
    client: httpx.AsyncClient, url: str, payload: dict[str, Any]
) -> list[float] | None:
    r = await client.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    # New API: 'embeddings' is a list of lists; Legacy: 'embedding' is a flat list
    emb = data.get("embedding")
    if not emb and "embeddings" in data:
        embs = data["embeddings"]
        if isinstance(embs, list) and len(embs) > 0:
            emb = embs[0]
    if not emb or not isinstance(emb, list):
        return None
    arr = np.asarray([float(x) for x in emb], dtype=np.float64).reshape(-1)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        return None
    n = float(np.linalg.norm(arr))
    if n < 1e-12:
        return None
    return (arr / n).tolist()


def http_fetch_ollama_embedding_with_policy(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
) -> np.ndarray | None:
    """
    Sync bridge: delegates to :func:`ahttp_fetch_ollama_embedding_with_policy`
    via ``asyncio.run()`` so that all HTTP I/O uses ``httpx.AsyncClient``.

    Must **not** be called from inside a running event loop; use the async
    variant directly in that case.
    """
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None  # type: ignore[assignment]

    if running is not None:
        import logging

        logging.getLogger(__name__).warning(
            "http_fetch_ollama_embedding_with_policy called from a running event loop. "
            "Use ahttp_fetch_ollama_embedding_with_policy instead. Returning None."
        )
        return None

    try:
        return asyncio.run(
            ahttp_fetch_ollama_embedding_with_policy(url, model, prompt, timeout_s=timeout_s)
        )
    except Exception as exc:
        _record_failure(repr(exc))
        return None


async def ahttp_fetch_ollama_embedding_with_policy(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
    aclient: httpx.AsyncClient | None = None,
) -> np.ndarray | None:
    """Async embedding fetch with cooperative backoff and circuit breaker."""
    t = (
        timeout_s
        if timeout_s is not None
        else max(1.0, _env_float("KERNEL_SEMANTIC_EMBED_TIMEOUT_S", 12.0))
    )
    retries = max(0, _env_int("KERNEL_SEMANTIC_EMBED_RETRIES", 2))
    backoff = max(0.0, _env_float("KERNEL_SEMANTIC_EMBED_BACKOFF_S", 0.25))

    if _circuit_blocks():
        return None

    # Auto-detect: try /api/embeddings first (legacy, more widely supported),
    # fall back to /api/embed (new API, Ollama >= 0.1.26).
    # The primary URL in the call should always end with one of these;
    # we derive the alt from it.
    if url.endswith("/api/embeddings"):
        # Primary = legacy endpoint (payload key: 'prompt')
        payload = {"model": model, "prompt": prompt}
    elif url.endswith("/api/embed"):
        # Primary = new endpoint (payload key: 'input')
        payload = {"model": model, "input": prompt}
    else:
        # Unknown path; keep payload as-is
        payload = {"model": model, "prompt": prompt}  # Default fallback payload
    last_err = ""
    for attempt in range(retries + 1):
        if _circuit_blocks():
            break
        t0 = time.perf_counter()
        try:
            httpx.Timeout(t)
            if aclient is not None:
                vec_list = await _apost_once(aclient, url, payload)
            else:
                client = await _get_aclient()
                vec_list = await _apost_once(client, url, payload)

            if vec_list is None:
                raise ValueError("missing or invalid embedding array")
            latency_ms = (time.perf_counter() - t0) * 1000.0
            _record_success(latency_ms)
            return np.asarray(vec_list, dtype=np.float64)
        except Exception as e:
            last_err = repr(e)
            if attempt < retries and backoff > 0:
                await asyncio.sleep(backoff * (attempt + 1))
    if last_err:
        _record_failure(last_err)
    return None


def maybe_hash_fallback_embedding(text: str) -> np.ndarray | None:
    """If policy allows (hash_fallback), return hash-scoped vector; else ``None``."""
    import os

    # KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=0 explicitly disables hash fallback regardless of policy.
    if os.environ.get("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "").strip() == "0":
        return None
    from src.modules.cognition.llm_touchpoint_policies import resolve_embedding_backend_policy

    policy = resolve_embedding_backend_policy()
    if policy == "hash_fallback":
        return hash_scoped_unit_embedding(text)
    return None
