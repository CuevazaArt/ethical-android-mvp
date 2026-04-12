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
from fastapi.testclient import TestClient
from src.chat_server import app
with TestClient(app) as c:
    r = c.get("/metrics")
    assert r.status_code == 200, r.text
    assert b"ethos_kernel" in r.content
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_health_includes_request_id_header():
    r = _client.get("/health", headers={"X-Request-ID": "test-req-1"})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == "test-req-1"
