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

from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

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

async def ahttp_fetch_ollama_embedding(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
) -> np.ndarray | None:
    """
    Async POST Ollama embeddings JSON; return unit L2 vector or ``None``.
    """
    return await ahttp_fetch_ollama_embedding_with_policy(url, model, prompt, timeout_s=timeout_s)


def _post_once(client: Any, url: str, payload: dict[str, Any]) -> list[float] | None:
    r = client.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    emb = data.get("embedding")
    if not emb or not isinstance(emb, list):
        return None
    arr = np.asarray([float(x) for x in emb], dtype=np.float64).reshape(-1)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        return None
    n = float(np.linalg.norm(arr))
    if n < 1e-12:
        return None
    return (arr / n).tolist()

async def _apost_once(client: httpx.AsyncClient, url: str, payload: dict[str, Any]) -> list[float] | None:
    r = await client.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    emb = data.get("embedding")
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
    import httpx

    t = (
        timeout_s
        if timeout_s is not None
        else max(1.0, _env_float("KERNEL_SEMANTIC_EMBED_TIMEOUT_S", 12.0))
    )
    retries = max(0, _env_int("KERNEL_SEMANTIC_EMBED_RETRIES", 2))
    backoff = max(0.0, _env_float("KERNEL_SEMANTIC_EMBED_BACKOFF_S", 0.25))

    if _circuit_blocks():
        return None

    payload = {"model": model, "prompt": prompt}
    last_err = ""
    for attempt in range(retries + 1):
        if _circuit_blocks():
            break
        t0 = time.perf_counter()
        try:
            with httpx.Client(timeout=t) as client:
                vec_list = _post_once(client, url, payload)
            if vec_list is None:
                raise ValueError("missing or invalid embedding array")
            latency_ms = (time.perf_counter() - t0) * 1000.0
            _record_success(latency_ms)
            return np.asarray(vec_list, dtype=np.float64)
        except Exception as e:
            last_err = repr(e)
            if attempt < retries and backoff > 0:
                time.sleep(backoff * (attempt + 1))
    if last_err:
        _record_failure(last_err)
    return None

async def ahttp_fetch_ollama_embedding_with_policy(
    url: str,
    model: str,
    prompt: str,
    *,
    timeout_s: float | None = None,
) -> np.ndarray | None:
    """Async variant of embedding fetch with cooperative backoff and circuit breaker."""
    import asyncio
    import httpx

    t = (
        timeout_s
        if timeout_s is not None
        else max(1.0, _env_float("KERNEL_SEMANTIC_EMBED_TIMEOUT_S", 12.0))
    )
    retries = max(0, _env_int("KERNEL_SEMANTIC_EMBED_RETRIES", 2))
    backoff = max(0.0, _env_float("KERNEL_SEMANTIC_EMBED_BACKOFF_S", 0.25))

    if _circuit_blocks():
        return None

    payload = {"model": model, "prompt": prompt}
    last_err = ""
    for attempt in range(retries + 1):
        if _circuit_blocks():
            break
        t0 = time.perf_counter()
        try:
            timeout = httpx.Timeout(t)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                emb = data.get("embedding")
                if not emb or not isinstance(emb, list):
                    raise ValueError("missing or invalid embedding array")
                
                arr = np.asarray([float(x) for x in emb], dtype=np.float64).reshape(-1)
                if arr.size == 0 or not np.all(np.isfinite(arr)):
                    raise ValueError("invalid embedding content")
                
                n = float(np.linalg.norm(arr))
                if n < 1e-12:
                    raise ValueError("zero-norm embedding")
                
                vec = arr / n
                latency_ms = (time.perf_counter() - t0) * 1000.0
                _record_success(latency_ms)
                return vec
        except Exception as e:
            last_err = repr(e)
            if attempt < retries and backoff > 0:
                await asyncio.sleep(backoff * (attempt + 1))
    if last_err:
        _record_failure(last_err)
    return None


def maybe_hash_fallback_embedding(text: str) -> np.ndarray | None:
    """If policy allows (hash_fallback), return hash-scoped vector; else ``None``."""
    from .llm_touchpoint_policies import resolve_embedding_backend_policy
    policy = resolve_embedding_backend_policy()
    if policy == "hash_fallback":
        return hash_scoped_unit_embedding(text)
    return None
