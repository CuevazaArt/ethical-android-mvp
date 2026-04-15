"""Prometheus /metrics endpoint."""

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from src.chat_server import app

_client = TestClient(app)


def test_metrics_disabled_by_default(monkeypatch):
    monkeypatch.delenv("KERNEL_METRICS", raising=False)
    r = _client.get("/metrics")
    assert r.status_code == 404
    assert r.json().get("error") == "metrics_disabled"


def test_metrics_prometheus_text_when_kernel_metrics_subprocess():
    """Fresh interpreter so ``KERNEL_METRICS`` is read at import time (lifespan + metric registration)."""
    pytest.importorskip("prometheus_client")
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
os.environ["KERNEL_METRICS"] = "1"
os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
os.environ["KERNEL_SEMANTIC_EMBED_HASH_FALLBACK"] = "1"
from fastapi.testclient import TestClient
from src.chat_server import app
from src.modules.semantic_chat_gate import run_semantic_malabs_after_lexical
with TestClient(app) as c:
    run_semantic_malabs_after_lexical("metrics probe benign hello", None)
    r = c.get("/metrics")
    assert r.status_code == 200, r.text
    assert b"ethos_kernel" in r.content
    assert b"ethos_kernel_semantic_malabs_outcomes_total" in r.content
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_chat_turn_async_timeout_counter_in_prometheus_subprocess():
    """Fresh interpreter: async-timeout counter increments (G-05 observability partial)."""
    pytest.importorskip("prometheus_client")
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
os.environ["KERNEL_METRICS"] = "1"
from src.observability.metrics import init_metrics, record_chat_turn_async_timeout
init_metrics()
record_chat_turn_async_timeout()
from prometheus_client import generate_latest
b = generate_latest().decode()
assert "ethos_kernel_chat_turn_async_timeouts_total" in b
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_health_includes_request_id_header():
    r = _client.get("/health", headers={"X-Request-ID": "test-req-1"})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == "test-req-1"


def test_kernel_process_metrics_in_prometheus_subprocess():
    """Fresh interpreter: kernel.process increments kernel decision + latency histograms."""
    pytest.importorskip("prometheus_client")
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
os.environ["KERNEL_METRICS"] = "1"
from src.observability.metrics import init_metrics
init_metrics()
from src.kernel import EthicalKernel
from src.modules.weighted_ethics_scorer import CandidateAction
k = EthicalKernel(variability=False, llm_mode="local")
acts = [
    CandidateAction("act_civically", "x", estimated_impact=0.5, confidence=0.8),
    CandidateAction("observe", "y", estimated_impact=0.0, confidence=0.9),
]
k.process("t", "here", {"risk": 0.1}, "everyday_ethics", acts, register_episode=False)
from prometheus_client import generate_latest
b = generate_latest().decode()
assert "ethos_kernel_kernel_decisions_total" in b
assert "ethos_kernel_kernel_process_seconds" in b
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)
