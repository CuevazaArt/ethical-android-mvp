"""V2.124 (C2): tests for the /api/feedback endpoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from src.core.feedback import FeedbackCalibrationLedger
from src.server import app as app_module


@pytest.fixture
def fresh_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    fresh = FeedbackCalibrationLedger(path=tmp_path / "ledger.jsonl")
    monkeypatch.setattr(app_module, "_feedback_ledger", fresh)
    return fresh


def test_feedback_endpoint_records_event(fresh_ledger):
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/feedback",
            json={
                "turn_id": "voice-1",
                "action": "comfort_user",
                "signal": 1,
            },
        )
    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is True
    assert body["stats"] == {"action": "comfort_user", "up": 1, "down": 0}


def test_feedback_endpoint_rejects_invalid_signal(fresh_ledger):
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/feedback",
            json={"turn_id": "x", "action": "y", "signal": 7},
        )
    body = response.json()
    assert response.status_code == 400
    assert body["ok"] is False
    assert body["error"]["code"] == "INVALID_FEEDBACK"


def test_feedback_endpoint_rejects_missing_action(fresh_ledger):
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/feedback",
            json={"turn_id": "x", "signal": 1},
        )
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "INVALID_FEEDBACK"


def test_feedback_endpoint_rejects_invalid_json(fresh_ledger):
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/feedback",
            data="not-json",
            headers={"Content-Type": "application/json"},
        )
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "INVALID_JSON"


def test_feedback_endpoint_reports_posterior_assisted_flag(
    fresh_ledger, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("KERNEL_BAYESIAN_MODE", "posterior_assisted")
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/feedback",
            json={"turn_id": "t", "action": "a", "signal": -1},
        )
    body = response.json()
    assert response.status_code == 200
    assert body["posterior_assisted"] is True
