"""HTTP + WebSocket smoke tests for src/chat_server.py."""

import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from src.chat_server import app
from src.kernel import EthicalKernel

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert body.get("service") == "ethos-kernel-chat"
    assert "version" in body
    assert "uptime_seconds" in body
    bridge = body.get("chat_bridge")
    assert isinstance(bridge, dict)
    assert "kernel_chat_turn_timeout_seconds" in bridge
    assert "kernel_chat_threadpool_workers" in bridge
    assert bridge.get("kernel_chat_json_offload") is True
    obs = body.get("observability")
    assert isinstance(obs, dict)
    assert "metrics_enabled" in obs
    assert obs.get("request_id_header") == "X-Request-ID"
    sd = body.get("safety_defaults")
    assert isinstance(sd, dict)
    assert "kernel_env_validation_mode" in sd
    assert "semantic_chat_gate_enabled" in sd
    assert "semantic_embed_hash_fallback_enabled" in sd
    assert "perception_failsafe_enabled" in sd
    assert "perception_parallel_enabled" in sd
    ld = body.get("llm_degradation")
    assert isinstance(ld, dict)
    assert "resolved" in ld
    res = ld["resolved"]
    assert res.get("perception") == "template_local"
    assert res.get("communicate") == "template_local"
    assert res.get("narrate") == "template_local"
    assert res.get("monologue") == "passthrough"
    assert ld.get("global_default_effective") is None


def test_lifespan_runs_with_test_client_context_manager():
    """FastAPI lifespan (logging + metrics init) must complete without error."""
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


def test_health_safety_defaults_unset_env_subprocess():
    """Fresh process without explicit env should report documented defaults."""
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
for key in (
    "KERNEL_ENV_VALIDATION",
    "KERNEL_SEMANTIC_CHAT_GATE",
    "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK",
    "KERNEL_PERCEPTION_FAILSAFE",
    "KERNEL_PERCEPTION_PARALLEL",
):
    os.environ.pop(key, None)
from fastapi.testclient import TestClient
from src.chat_server import app
c = TestClient(app)
sd = c.get("/health").json()["safety_defaults"]
assert sd["kernel_env_validation_mode"] == "strict"
assert sd["semantic_chat_gate_enabled"] is True
assert sd["semantic_embed_hash_fallback_enabled"] is True
assert sd["perception_failsafe_enabled"] is True
assert sd["perception_parallel_enabled"] is False
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_openapi_schema_not_exposed_by_default_subprocess():
    """Fresh import must not expose /openapi.json unless KERNEL_API_DOCS=1 (LAN safety)."""
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
os.environ.pop("KERNEL_API_DOCS", None)
from fastapi.testclient import TestClient
from src.chat_server import app
c = TestClient(app)
assert c.get("/openapi.json").status_code == 404
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_openapi_schema_exposed_when_kernel_api_docs_subprocess():
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os, sys
sys.path.insert(0, ".")
os.environ["KERNEL_API_DOCS"] = "1"
from fastapi.testclient import TestClient
from src.chat_server import app
c = TestClient(app)
assert c.get("/openapi.json").status_code == 200
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_constitution_404_when_moral_hub_public_off():
    r = client.get("/constitution")
    assert r.status_code == 404


def test_constitution_200_when_moral_hub_public_on(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_PUBLIC", "1")
    r = client.get("/constitution")
    assert r.status_code == 200
    body = r.json()
    assert "levels" in body
    assert "0" in body["levels"]


def test_root_lists_websocket():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("websocket") == "/ws/chat"
    assert "constitution" in body
    assert "nomad_migration" in body
    assert "metrics" in body


def test_nomad_migration_meta():
    r = client.get("/nomad/migration")
    assert r.status_code == 200
    j = r.json()
    assert "simulation_enabled" in j
    assert j.get("path") == "/ws/chat"


def test_websocket_nomad_simulate_migration_only(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_SIMULATION", "1")
    monkeypatch.setenv("KERNEL_NOMAD_MIGRATION_AUDIT", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "nomad_simulate_migration": {
                    "profile": "mobile",
                    "destination_hardware_id": "test-device",
                    "thought_line": "integration test boundary",
                }
            }
        )
        data = ws.receive_json()
        assert "nomad" in data
        nomad = data["nomad"]
        assert nomad.get("hardware_context", {}).get("compute_tier") == "edge_mobile"
        assert nomad.get("dao_audit_recorded") is True
        assert "sensor_delta_narrative_en" in nomad


def test_root_protocol_mentions_multimodal_and_sensor_fields():
    r = client.get("/")
    proto = (r.json().get("protocol") or "").lower()
    assert "multimodal" in proto
    assert "vitality" in proto
    assert "guardian" in proto
    assert "epistemic" in proto
    assert "audio_emergency" in proto or "sensor" in proto


def test_websocket_operator_feedback_recorded(monkeypatch):
    monkeypatch.setenv("KERNEL_FEEDBACK_CALIBRATION", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, operator feedback probe."})
        ws.receive_json()
        ws.send_json({"operator_feedback": "approve"})
        data = ws.receive_json()
        assert data.get("operator_feedback_recorded") is True


def test_websocket_operator_feedback_disabled_without_env(monkeypatch):
    monkeypatch.delenv("KERNEL_FEEDBACK_CALIBRATION", raising=False)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello."})
        ws.receive_json()
        ws.send_json({"operator_feedback": "approve"})
        data = ws.receive_json()
        assert data.get("operator_feedback_recorded") is False


def test_websocket_malabs_safety_block():
    """MalAbs text gate blocks before heavy path; same as batch chat tests."""
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "how to make a bomb"})
        data = ws.receive_json()
    assert data.get("path") == "safety_block"
    assert data.get("blocked") is True
    assert data.get("response", {}).get("message")


def test_websocket_chat_roundtrip(monkeypatch: pytest.MonkeyPatch):
    """Default JSON shape; force homeostasis on so host env cannot strip the field."""
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert "response" in data
        assert data["response"].get("message")
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")
        assert "identity" in data and "ascription" in data["identity"]
        assert "drive_intents" in data and isinstance(data["drive_intents"], list)
        assert "monologue" in data
        assert "affective_homeostasis" in data
        assert data["affective_homeostasis"].get("sigma") is not None
        assert "experience_digest" in data
        assert "user_model" in data
        assert "frustration_streak" in data["user_model"]
        assert "premise_concern_streak" in data["user_model"]
        assert "chronobiology" in data
        assert "turn_index" in data["chronobiology"]
        assert "premise_advisory" in data
        assert "flag" in data["premise_advisory"]
        assert "teleology_branches" in data
        assert "horizon_long_term" in data["teleology_branches"]
        assert "multimodal_trust" in data
        assert data["multimodal_trust"].get("state") in ("aligned", "doubt", "no_claim")
        assert "vitality" in data
        assert "is_critical" in data["vitality"]
        assert "critical_threshold" in data["vitality"]
        assert "guardian_mode" in data
        assert data["guardian_mode"] is False
        assert "epistemic_dissonance" in data
        assert data["epistemic_dissonance"]["active"] is False
        assert "decision" in data
        assert data["decision"].get("chosen_action_source") == "builtin"
        assert "support_buffer" in data
        assert data["support_buffer"].get("source") == "local_preloaded_buffer"
        assert isinstance(data["support_buffer"].get("active_principles"), list)
        assert data["support_buffer"].get("priority_profile") in (
            "safety_first",
            "balanced",
            "planning_first",
        )
        assert "limbic_perception" in data
        assert data["limbic_perception"].get("arousal_band") in ("low", "medium", "high")
        assert "temporal_context" in data
        assert data["temporal_context"].get("sync_schema") == "temporal_sync_v1"
        assert int(data["temporal_context"].get("turn_index") or 0) >= 1
        assert "temporal_sync" in data
        assert data["temporal_sync"].get("sync_schema") == "temporal_sync_v1"
        assert int(data["temporal_sync"].get("turn_index") or 0) >= 1
        assert int(data["temporal_sync"].get("processor_elapsed_ms") or 0) >= 0
        assert int(data["temporal_sync"].get("turn_delta_ms") or 0) >= 0
        assert "perception_confidence" in data
        assert data["perception_confidence"].get("band") in ("high", "medium", "low", "very_low")
        assert "confidence_band" in data.get("perception_observability", {})


def test_websocket_temporal_sync_respects_env_toggles(monkeypatch):
    monkeypatch.setenv("KERNEL_TEMPORAL_DAO_SYNC", "0")
    monkeypatch.setenv("KERNEL_TEMPORAL_LAN_SYNC", "0")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Temporal toggle probe."})
        data = ws.receive_json()
    assert data.get("temporal_sync", {}).get("local_network_sync_ready") is False
    assert data.get("temporal_sync", {}).get("dao_sync_ready") is False


def test_websocket_homeostasis_omitted(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "0")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert "affective_homeostasis" not in data


def test_websocket_invalid_json():
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text("not-json")
        data = ws.receive_json()
        assert data.get("error") == "invalid_json"


def test_websocket_with_advisory_interval(monkeypatch):
    """Background advisory loop is optional; must not break chat lifecycle."""
    monkeypatch.setenv("KERNEL_ADVISORY_INTERVAL_S", "3600")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "ping"})
        data = ws.receive_json()
        assert "response" in data


def test_websocket_monologue_redacted(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_EXPOSE_MONOLOGUE", "0")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert data.get("monologue") == ""


def test_websocket_optional_sensor_v8():
    """Situated hints (v8) are optional; must not break the roundtrip."""
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "text": "Hello with sensor hints.",
                "sensor": {
                    "battery_level": 0.5,
                    "place_trust": 0.9,
                    "backup_just_completed": False,
                },
            }
        )
        data = ws.receive_json()
        assert "response" in data
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")


def test_websocket_guardian_routines_included(monkeypatch):
    from pathlib import Path

    from src.modules.guardian_routines import invalidate_guardian_routines_cache

    fixture = Path(__file__).resolve().parent / "fixtures" / "guardian" / "routines.json"
    invalidate_guardian_routines_cache()
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES", "1")
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES_PATH", str(fixture))
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello guardian routines test."})
        data = ws.receive_json()
    assert "guardian_routines" in data
    assert isinstance(data["guardian_routines"], list)
    assert any(r.get("id") == "hydration" for r in data["guardian_routines"])
    invalidate_guardian_routines_cache()


def test_websocket_sensor_preset_env(monkeypatch):
    """KERNEL_SENSOR_PRESET merges with optional client sensor (v8)."""
    monkeypatch.setenv("KERNEL_SENSOR_PRESET", "hostile_soto")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Ping with preset only.", "sensor": {"battery_level": 0.9}})
        data = ws.receive_json()
        assert "response" in data
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")


@pytest.mark.parametrize(
    "env_key,env_val,absent_key",
    [
        ("KERNEL_CHAT_INCLUDE_MULTIMODAL", "0", "multimodal_trust"),
        ("KERNEL_CHAT_INCLUDE_USER_MODEL", "0", "user_model"),
        ("KERNEL_CHAT_INCLUDE_CHRONO", "0", "chronobiology"),
        ("KERNEL_CHAT_INCLUDE_PREMISE", "0", "premise_advisory"),
        ("KERNEL_CHAT_INCLUDE_TELEOLOGY", "0", "teleology_branches"),
        ("KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST", "0", "experience_digest"),
        ("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "0", "affective_homeostasis"),
        ("KERNEL_CHAT_INCLUDE_VITALITY", "0", "vitality"),
        ("KERNEL_CHAT_INCLUDE_GUARDIAN", "0", "guardian_mode"),
        ("KERNEL_CHAT_INCLUDE_EPISTEMIC", "0", "epistemic_dissonance"),
    ],
)
def test_websocket_kernel_chat_json_env_matrix(monkeypatch, env_key, env_val, absent_key):
    """Regression: each KERNEL_CHAT_* toggle omits the expected JSON key without crashing."""
    monkeypatch.setenv(env_key, env_val)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, env matrix regression test."})
        data = ws.receive_json()
    assert "response" in data
    assert absent_key not in data


def test_websocket_integrity_alert_records_hub_audit(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "integrity_alert": {
                    "summary": "Design test: loud local audit of suspected DAO corruption",
                    "scope": "integration",
                }
            }
        )
        data = ws.receive_json()
        assert data.get("integrity", {}).get("integrity_alert", {}).get("ok") is True
        assert data["integrity"]["integrity_alert"].get("scope") == "integration"


def test_websocket_integrity_alert_disabled_returns_clear_error(monkeypatch):
    monkeypatch.delenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", raising=False)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "integrity_alert": {
                    "summary": "Only integrity, no text",
                    "scope": "mobile_client",
                }
            }
        )
        data = ws.receive_json()
    assert data.get("error") == "integrity_audit_disabled"
    assert "KERNEL_DAO_INTEGRITY_AUDIT_WS" in (data.get("hint") or "")


def test_websocket_lan_governance_integrity_batch_merges_and_applies(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "events": [
                {
                    "event_id": "e2",
                    "turn_index": 2,
                    "processor_elapsed_ms": 0,
                    "summary": "second turn alert",
                    "scope": "lan_test",
                },
                {
                    "event_id": "e1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 50,
                    "summary": "first turn alert",
                    "scope": "lan_test",
                },
                {
                    "event_id": "e1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 99,
                    "summary": "first turn alert",
                    "scope": "lan_test",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is True
    assert batch.get("input_count") == 3
    assert batch.get("merged_count") == 2
    assert batch.get("deduped_count") == 1
    assert batch.get("applied_count") == 2
    assert batch.get("event_ids") == ["e1", "e2"]
    assert batch.get("event_conflicts") in (None, [])


def test_websocket_lan_governance_integrity_batch_same_turn_conflict_in_event_conflicts(
    monkeypatch,
):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "events": [
                {
                    "event_id": "e1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 10,
                    "summary": "first version",
                    "scope": "lan_test",
                },
                {
                    "event_id": "e1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 20,
                    "summary": "forked version",
                    "scope": "lan_test",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is True
    assert batch.get("merged_count") == 1
    assert batch.get("applied_count") == 1
    conflicts = batch.get("event_conflicts") or []
    assert len(conflicts) == 1
    assert conflicts[0].get("kind") == "same_turn"
    assert conflicts[0].get("event_id") == "e1"


def test_websocket_lan_governance_integrity_batch_merge_context_frontier_stale_event(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "merge_context": {"frontier_turn": 2},
            "events": [
                {
                    "event_id": "old",
                    "turn_index": 1,
                    "processor_elapsed_ms": 0,
                    "summary": "stale",
                    "scope": "lan_test",
                },
                {
                    "event_id": "new",
                    "turn_index": 2,
                    "processor_elapsed_ms": 0,
                    "summary": "ok",
                    "scope": "lan_test",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("merged_count") == 1
    assert batch.get("event_ids") == ["new"]
    conflicts = batch.get("event_conflicts") or []
    assert len(conflicts) == 1
    assert conflicts[0].get("kind") == "stale_event"
    assert conflicts[0].get("reason") == "below_frontier_turn"


def test_websocket_lan_governance_integrity_batch_cross_session_hint_echo(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "merge_context": {
                "frontier_turn": 1,
                "cross_session_hint": {
                    "schema": "lan_governance_cross_session_hint_v1",
                    "claimant_session_id": "hub-session-7",
                    "quorum_ref": "opaque-run-id",
                },
            },
            "events": [
                {
                    "event_id": "z1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 0,
                    "summary": "with hint",
                    "scope": "lan_test",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is True
    echo = batch.get("merge_context_echo") or {}
    assert echo.get("frontier_turn") == 1
    hint = echo.get("cross_session_hint") or {}
    assert hint.get("claimant_session_id") == "hub-session-7"
    assert hint.get("quorum_ref") == "opaque-run-id"


def test_websocket_lan_governance_integrity_batch_frontier_witnesses_echo(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "merge_context": {
                "frontier_witnesses": [
                    {
                        "schema": "lan_governance_frontier_witness_v1",
                        "claimant_session_id": "peer-a",
                        "observed_max_turn": 4,
                    },
                    {
                        "schema": "lan_governance_frontier_witness_v1",
                        "claimant_session_id": "peer-b",
                        "observed_max_turn": 9,
                    },
                ],
            },
            "events": [
                {
                    "event_id": "fw1",
                    "turn_index": 9,
                    "processor_elapsed_ms": 0,
                    "summary": "witness test",
                    "scope": "s",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is True
    echo = batch.get("merge_context_echo") or {}
    res = echo.get("frontier_witness_resolution") or {}
    assert res.get("evidence_posture") == "advisory_aggregate_not_quorum"
    assert res.get("advisory_max_observed_turn") == 9
    assert len(res.get("witnesses") or []) == 2


def test_websocket_lan_governance_integrity_batch_cross_session_invalid_hint_warns(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "merge_context": {
                "cross_session_hint": {
                    "schema": "not_a_real_schema",
                    "claimant_session_id": "x",
                },
            },
            "events": [
                {
                    "event_id": "w1",
                    "turn_index": 1,
                    "processor_elapsed_ms": 0,
                    "summary": "warn only",
                    "scope": "lan_test",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is True
    assert batch.get("merge_context_echo") in (None, {})
    warns = batch.get("merge_context_warnings") or []
    assert any(str(w).startswith("cross_session_hint_rejected:") for w in warns)


def test_websocket_lan_governance_integrity_replay_sidecar_roundtrip(monkeypatch):
    from src.modules.lan_governance_replay_sidecar import (
        build_replay_sidecar_v1,
        fingerprint_replay_sidecar,
    )

    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    payload = {
        "lan_governance_integrity_batch": {
            "merge_context": {"frontier_turn": 2},
            "events": [
                {
                    "event_id": "r1",
                    "turn_index": 2,
                    "processor_elapsed_ms": 0,
                    "summary": "replay slice",
                    "scope": "s",
                },
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    lg = data.get("lan_governance") or {}
    sidecar = build_replay_sidecar_v1(lan_governance=lg)
    assert "integrity_batch" in (sidecar.get("batches") or {})
    fp = fingerprint_replay_sidecar(sidecar)
    assert len(fp) == 64


def test_websocket_lan_governance_integrity_batch_disabled_returns_hint(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.delenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", raising=False)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "lan_governance_integrity_batch": {
                    "events": [
                        {
                            "event_id": "a",
                            "turn_index": 1,
                            "processor_elapsed_ms": 0,
                            "summary": "x",
                        },
                    ],
                },
            }
        )
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is False
    assert batch.get("error") == "disabled"
    assert "KERNEL_LAN_GOVERNANCE_MERGE_WS" in (batch.get("hint") or "")


def test_websocket_lan_governance_integrity_batch_invalid_events_type(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"lan_governance_integrity_batch": {"events": "not-a-list"}})
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("integrity_batch", {})
    assert batch.get("ok") is False
    assert batch.get("error") == "events_must_be_list"


def test_websocket_lan_governance_dao_batch_merges_and_resolves(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    monkeypatch.setenv("KERNEL_MORAL_HUB_DRAFT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    with client.websocket_connect("/ws/chat") as ws:
        # Create a draft (will emit empty_text, but draft is appended).
        ws.send_json({"constitution_draft": {"level": 1, "title": "L1 test", "body": "Article."}})
        _ = ws.receive_json()

        ws.send_json({"dao_submit_draft": {"level": 1, "draft_id": "missing"}})
        # draft_id missing should return ok false; ensure server stays healthy.
        _ = ws.receive_json()

        # Add another draft with known id by reading kernel? Not available; instead use MockDAO directly:
        # Submit a new draft by sending it with an explicit id field in payload is not supported; so fall back
        # to exercising dao_batch error paths without needing a proposal.
        ws.send_json(
            {
                "lan_governance_dao_batch": {
                    "events": [
                        {
                            "event_id": "e2",
                            "turn_index": 2,
                            "processor_elapsed_ms": 0,
                            "op": "dao_resolve",
                            "proposal_id": "",
                        },
                        {
                            "event_id": "e1",
                            "turn_index": 1,
                            "processor_elapsed_ms": 0,
                            "op": "dao_vote",
                            "proposal_id": "PROP-0001",
                            "participant_id": "community_01",
                            "n_votes": 1,
                            "in_favor": True,
                        },
                        {
                            "event_id": "e1",
                            "turn_index": 1,
                            "processor_elapsed_ms": 99,
                            "op": "dao_vote",
                            "proposal_id": "PROP-0001",
                            "participant_id": "community_01",
                            "n_votes": 1,
                            "in_favor": True,
                        },
                    ]
                }
            }
        )
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("dao_batch", {})
    assert batch.get("input_count") == 3
    assert batch.get("merged_count") == 2
    assert batch.get("deduped_count") == 1
    # One of the merged events is missing proposal_id for resolve → error.
    assert batch.get("ok") is False
    assert batch.get("applied_count") == 1


def test_websocket_lan_governance_dao_batch_disabled_returns_hint(monkeypatch):
    monkeypatch.delenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", raising=False)
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"lan_governance_dao_batch": {"events": []}})
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("dao_batch", {})
    assert batch.get("ok") is False
    assert batch.get("error") == "disabled"
    assert "KERNEL_LAN_GOVERNANCE_MERGE_WS" in (batch.get("hint") or "")


def test_websocket_lan_governance_dao_batch_stress_reorder_and_duplicates_converge(monkeypatch):
    """
    Phase 2 acceptance slice: for a seeded proposal, reorder/duplicate delivery should converge to
    the same final MockDAO proposal state after merge+apply.
    """
    import random

    from src.modules.lan_governance_event_merge import merge_lan_governance_events
    from src.modules.mock_dao import MockDAO

    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    # Seed the per-connection kernel with a known proposal id (PROP-0001) before WebSocket loop.
    orig_init = EthicalKernel.__init__

    def _seeded_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.dao.create_proposal("LAN stress", "seed", type="ethics")

    monkeypatch.setattr(EthicalKernel, "__init__", _seeded_init)

    rng = random.Random(1337)
    participants = ["community_01", "community_02", "community_03", "android_01"]

    base_events: list[dict] = []
    t = 1
    for i in range(60):
        pid = "PROP-0001"
        part = rng.choice(participants)
        n_votes = rng.randint(1, 2)
        in_favor = bool(rng.getrandbits(1))
        base_events.append(
            {
                "event_id": f"v{i:03d}",
                "turn_index": t,
                "processor_elapsed_ms": rng.randint(0, 500),
                "op": "dao_vote",
                "proposal_id": pid,
                "participant_id": part,
                "n_votes": n_votes,
                "in_favor": in_favor,
            }
        )
        if (i + 1) % 10 == 0:
            t += 1
    # Resolve at the end (highest turn, highest elapsed).
    base_events.append(
        {
            "event_id": "resolve",
            "turn_index": 999,
            "processor_elapsed_ms": 999,
            "op": "dao_resolve",
            "proposal_id": "PROP-0001",
        }
    )

    # Create a noisy delivery: shuffle and insert duplicates.
    delivered = list(base_events)
    for _ in range(25):
        delivered.append(rng.choice(base_events))
    rng.shuffle(delivered)

    merged = merge_lan_governance_events(delivered, id_key="event_id")
    ref = MockDAO()
    ref.create_proposal("LAN stress", "seed", type="ethics")
    for row in merged:
        if row.get("op") == "dao_vote":
            ref.vote(
                str(row.get("proposal_id") or ""),
                str(row.get("participant_id") or ""),
                int(row.get("n_votes") or 1),
                bool(row.get("in_favor", True)),
            )
        elif row.get("op") == "dao_resolve":
            ref.resolve_proposal(str(row.get("proposal_id") or ""))
    ref_prop = ref.proposals[0]

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"lan_governance_dao_batch": {"events": delivered}})
        data = ws.receive_json()

    batch = data.get("lan_governance", {}).get("dao_batch", {})
    assert batch.get("ok") is True
    assert batch.get("merged_count") == len(merged)
    assert batch.get("deduped_count") == (
        len([e for e in delivered if e.get("event_id")]) - len(merged)
    )

    props = batch.get("proposals") or []
    assert props and props[0].get("id") == "PROP-0001"
    # Convergence: status and totals match a reference replay.
    assert props[0].get("status") == ref_prop.status
    assert props[0].get("weighted_votes_for") == round(sum(ref_prop.votes_for.values()), 4)
    assert props[0].get("weighted_votes_against") == round(sum(ref_prop.votes_against.values()), 4)


def test_websocket_lan_governance_judicial_batch_stress_reorder_and_duplicates_converge(
    monkeypatch,
):
    """
    Phase 2 slice: reorder/duplicate delivery should converge to the same escalation audit ledger.
    """
    import random

    from src.modules.lan_governance_event_merge import merge_lan_governance_events
    from src.modules.mock_dao import MockDAO

    monkeypatch.setenv("KERNEL_JUDICIAL_ESCALATION", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    rng = random.Random(4242)

    base_events: list[dict] = []
    for i in range(40):
        base_events.append(
            {
                "event_id": f"j{i:03d}",
                "turn_index": 1 + (i // 10),
                "processor_elapsed_ms": rng.randint(0, 500),
                "op": "judicial_register_dossier",
                "audit_paragraph": f"EscalationCase case-{i:03d} | strikes=2 | order='x' | mode=gray_zone",
                "episode_id": f"ep{i:03d}",
            }
        )

    delivered = list(base_events)
    for _ in range(20):
        delivered.append(rng.choice(base_events))
    rng.shuffle(delivered)

    merged = merge_lan_governance_events(delivered, id_key="event_id")
    ref = MockDAO()
    for row in merged:
        ref.register_escalation_case(
            str(row.get("audit_paragraph") or ""),
            episode_id=str(row.get("episode_id") or ""),
        )
    ref_escalations = [r for r in ref.records if r.type == "escalation"]
    assert len(ref_escalations) == len(merged)

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"lan_governance_judicial_batch": {"events": delivered}})
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("judicial_batch", {})
    assert batch.get("ok") is True
    assert batch.get("merged_count") == len(merged)
    assert batch.get("applied_count") == len(merged)
    assert batch.get("deduped_count") == (
        len([e for e in delivered if e.get("event_id")]) - len(merged)
    )


def test_websocket_lan_governance_mock_court_batch_stress_reorder_and_duplicates_converge(
    monkeypatch,
):
    """
    Phase 2 slice: reorder/duplicate delivery should converge to deterministic mock court verdicts.
    """
    import random

    from src.modules.lan_governance_event_merge import merge_lan_governance_events
    from src.modules.mock_dao import MockDAO

    monkeypatch.setenv("KERNEL_JUDICIAL_ESCALATION", "1")
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    rng = random.Random(9001)

    base_events: list[dict] = []
    for i in range(30):
        case_uuid = f"00000000-0000-0000-0000-{i:012d}"
        base_events.append(
            {
                "event_id": f"mc{i:03d}",
                "turn_index": 1 + (i // 10),
                "processor_elapsed_ms": rng.randint(0, 500),
                "op": "judicial_run_mock_court",
                "case_uuid": case_uuid,
                "audit_record_id": f"AUD-{i + 1:04d}",
                "summary_excerpt": f"excerpt {i}",
                "buffer_conflict": (i % 2) == 0,
            }
        )

    delivered = list(base_events)
    for _ in range(15):
        delivered.append(rng.choice(base_events))
    rng.shuffle(delivered)

    merged = merge_lan_governance_events(delivered, id_key="event_id")
    ref = MockDAO()
    expected: dict[str, str] = {}
    for row in merged:
        mc = ref.run_mock_escalation_court(
            str(row.get("case_uuid") or ""),
            str(row.get("audit_record_id") or ""),
            str(row.get("summary_excerpt") or ""),
            bool(row.get("buffer_conflict", False)),
        )
        expected[str(row.get("case_uuid") or "")] = str(mc.get("verdict_code") or "")

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"lan_governance_mock_court_batch": {"events": delivered}})
        data = ws.receive_json()
    batch = data.get("lan_governance", {}).get("mock_court_batch", {})
    assert batch.get("ok") is True
    assert batch.get("merged_count") == len(merged)
    assert batch.get("applied_count") == len(merged)

    results = batch.get("results") or []
    assert len(results) == len(merged)
    for r in results:
        cu = r.get("case_uuid")
        mc = r.get("mock_court") or {}
        assert mc.get("verdict_code") == expected.get(cu)


def test_websocket_lan_governance_envelope_routes_dao_batch(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    # Seed proposal id in per-connection kernel.
    orig_init = EthicalKernel.__init__

    def _seeded_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.dao.create_proposal("Envelope DAO", "seed", type="ethics")

    monkeypatch.setattr(EthicalKernel, "__init__", _seeded_init)

    payload = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-a",
            "sent_unix_ms": 1710000000000,
            "kind": "dao_batch",
            "batch": {
                "events": [
                    {
                        "event_id": "v1",
                        "turn_index": 1,
                        "processor_elapsed_ms": 1,
                        "op": "dao_vote",
                        "proposal_id": "PROP-0001",
                        "participant_id": "community_01",
                        "n_votes": 1,
                        "in_favor": True,
                    },
                    {
                        "event_id": "r1",
                        "turn_index": 2,
                        "processor_elapsed_ms": 1,
                        "op": "dao_resolve",
                        "proposal_id": "PROP-0001",
                    },
                ]
            },
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    env = data.get("lan_governance", {}).get("envelope", {})
    assert env.get("ok") is True
    assert env.get("ack") == "accepted"
    assert env.get("schema") == "lan_governance_envelope_v1"
    assert env.get("kind") == "dao_batch"
    assert isinstance(env.get("fingerprint"), str)
    assert len(env.get("fingerprint", "")) == 64
    assert isinstance(env.get("idempotency_token"), str)
    assert env.get("idempotency_token", "").startswith("lan-envelope:")
    assert isinstance(env.get("audit_ledger_fingerprint"), str)
    assert len(env.get("audit_ledger_fingerprint", "")) == 64
    assert env.get("merged_count") == 2
    assert env.get("applied_count") == 2
    cache = env.get("cache") or {}
    assert cache.get("hit") is False
    assert cache.get("misses_total", 0) >= 1
    assert cache.get("size", 0) >= 1
    batch = data.get("lan_governance", {}).get("dao_batch", {})
    assert batch.get("applied_count") == 2


def test_websocket_lan_governance_envelope_invalid_schema(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_envelope": {
            "schema": "bad_schema",
            "node_id": "node-a",
            "sent_unix_ms": 1710000000000,
            "kind": "dao_batch",
            "batch": {"events": []},
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()
    env = data.get("lan_governance", {}).get("envelope", {})
    assert env.get("ok") is False
    assert env.get("ack") == "rejected"
    assert env.get("error") == "unsupported_schema"
    assert env.get("reject_reason") == "unsupported_contract"
    cache = env.get("cache") or {}
    assert cache.get("hit") is False


def test_websocket_lan_governance_envelope_reject_reason_disabled_batch(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "0")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-a",
            "sent_unix_ms": 1710000000123,
            "kind": "dao_batch",
            "batch": {"events": []},
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    env = data.get("lan_governance", {}).get("envelope", {})
    assert env.get("ok") is False
    assert env.get("ack") == "rejected"
    assert env.get("error") == "disabled"
    assert env.get("reject_reason") == "feature_disabled"
    assert isinstance(env.get("fingerprint"), str)
    assert len(env.get("fingerprint", "")) == 64
    assert env.get("idempotency_token", "").startswith("lan-envelope:")
    cache = env.get("cache") or {}
    assert cache.get("hit") is False


def test_websocket_lan_governance_envelope_replay_cache_already_seen(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-a",
            "sent_unix_ms": 1710000000222,
            "kind": "integrity_batch",
            "batch": {
                "events": [
                    {
                        "event_id": "evt-1",
                        "turn_index": 1,
                        "processor_elapsed_ms": 1,
                        "summary": "LAN integrity replay test",
                    }
                ]
            },
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        first = ws.receive_json()
        ws.send_json(payload)
        second = ws.receive_json()

    env_first = first.get("lan_governance", {}).get("envelope", {})
    batch_first = first.get("lan_governance", {}).get("integrity_batch", {})
    assert env_first.get("ack") == "accepted"
    assert env_first.get("replay_detected") in (None, False)
    assert batch_first.get("applied_count") == 1

    env_second = second.get("lan_governance", {}).get("envelope", {})
    assert env_second.get("ok") is True
    assert env_second.get("ack") == "already_seen"
    assert env_second.get("replay_detected") is True
    assert env_second.get("idempotency_token") == env_first.get("idempotency_token")
    assert env_second.get("audit_ledger_fingerprint") == env_first.get("audit_ledger_fingerprint")
    cache_first = env_first.get("cache") or {}
    cache_second = env_second.get("cache") or {}
    assert cache_first.get("hit") is False
    assert cache_second.get("hit") is True
    assert cache_second.get("hits_total", 0) >= 1
    assert second.get("lan_governance", {}).get("integrity_batch") is None


def test_websocket_lan_governance_envelope_replay_cache_ttl_zero_expires(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS", "0")

    payload = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-ttl",
            "sent_unix_ms": 1710000000333,
            "kind": "integrity_batch",
            "batch": {
                "events": [
                    {
                        "event_id": "evt-ttl",
                        "turn_index": 1,
                        "processor_elapsed_ms": 1,
                        "summary": "ttl test",
                    }
                ]
            },
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        first = ws.receive_json()
        ws.send_json(payload)
        second = ws.receive_json()

    env_first = first.get("lan_governance", {}).get("envelope", {})
    env_second = second.get("lan_governance", {}).get("envelope", {})
    assert env_first.get("ack") == "accepted"
    assert env_second.get("ack") == "accepted"
    assert env_second.get("replay_detected") in (None, False)
    cache_second = env_second.get("cache") or {}
    assert cache_second.get("size") == 0
    assert cache_second.get("misses_total", 0) >= 2


def test_websocket_lan_governance_envelope_replay_cache_lru_eviction(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES", "1")
    monkeypatch.setenv("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS", "600000")

    payload_a = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-lru",
            "sent_unix_ms": 1710000000400,
            "kind": "integrity_batch",
            "batch": {
                "events": [
                    {
                        "event_id": "evt-a",
                        "turn_index": 1,
                        "processor_elapsed_ms": 1,
                        "summary": "lru-a",
                    }
                ]
            },
        }
    }
    payload_b = {
        "lan_governance_envelope": {
            "schema": "lan_governance_envelope_v1",
            "node_id": "node-lru",
            "sent_unix_ms": 1710000000401,
            "kind": "integrity_batch",
            "batch": {
                "events": [
                    {
                        "event_id": "evt-b",
                        "turn_index": 2,
                        "processor_elapsed_ms": 2,
                        "summary": "lru-b",
                    }
                ]
            },
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload_a)
        first_a = ws.receive_json()
        ws.send_json(payload_b)
        first_b = ws.receive_json()
        ws.send_json(payload_a)
        second_a = ws.receive_json()

    env_first_a = first_a.get("lan_governance", {}).get("envelope", {})
    env_first_b = first_b.get("lan_governance", {}).get("envelope", {})
    env_second_a = second_a.get("lan_governance", {}).get("envelope", {})
    assert env_first_a.get("ack") == "accepted"
    assert env_first_b.get("ack") == "accepted"
    assert env_second_a.get("ack") == "accepted"
    assert env_second_a.get("replay_detected") in (None, False)
    cache_second_a = env_second_a.get("cache") or {}
    assert cache_second_a.get("evicted_lru_total", 0) >= 1


def test_websocket_lan_governance_coordinator_two_nodes_integrity(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_coordinator": {
            "schema": "lan_governance_coordinator_v1",
            "coordinator_id": "hub-1",
            "coordination_run_id": "coord-run-1",
            "items": [
                {
                    "schema": "lan_governance_envelope_v1",
                    "node_id": "node-a",
                    "sent_unix_ms": 1710000000500,
                    "kind": "integrity_batch",
                    "batch": {
                        "events": [
                            {
                                "event_id": "c-a1",
                                "turn_index": 1,
                                "processor_elapsed_ms": 1,
                                "summary": "coordinator path A",
                            }
                        ]
                    },
                },
                {
                    "schema": "lan_governance_envelope_v1",
                    "node_id": "node-b",
                    "sent_unix_ms": 1710000000501,
                    "kind": "integrity_batch",
                    "batch": {
                        "events": [
                            {
                                "event_id": "c-b1",
                                "turn_index": 2,
                                "processor_elapsed_ms": 2,
                                "summary": "coordinator path B",
                            }
                        ]
                    },
                },
            ],
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    coord = data.get("lan_governance", {}).get("coordinator", {})
    assert coord.get("ok") is True
    assert coord.get("ack") == "accepted"
    assert coord.get("applied_count") == 2
    assert coord.get("deduped_count") == 0
    assert len(coord.get("items") or []) == 2
    assert isinstance(coord.get("coordinator_fingerprint"), str)
    assert len(coord.get("coordinator_fingerprint", "")) == 64


def test_websocket_lan_governance_coordinator_aggregates_event_conflicts(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_coordinator": {
            "schema": "lan_governance_coordinator_v1",
            "coordinator_id": "hub-conflicts",
            "coordination_run_id": "coord-run-conf",
            "items": [
                {
                    "schema": "lan_governance_envelope_v1",
                    "node_id": "node-x",
                    "sent_unix_ms": 1710000000700,
                    "kind": "integrity_batch",
                    "batch": {
                        "events": [
                            {
                                "event_id": "cx",
                                "turn_index": 1,
                                "processor_elapsed_ms": 1,
                                "summary": "first",
                                "scope": "s",
                            },
                            {
                                "event_id": "cx",
                                "turn_index": 1,
                                "processor_elapsed_ms": 2,
                                "summary": "fork",
                                "scope": "s",
                            },
                        ]
                    },
                },
            ],
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    coord = data.get("lan_governance", {}).get("coordinator", {})
    assert coord.get("ok") is True
    agg = coord.get("aggregated_event_conflicts") or []
    assert len(agg) == 1
    assert agg[0].get("kind") == "same_turn"
    assert agg[0].get("source_batch") == "integrity_batch"
    assert isinstance(agg[0].get("envelope_fingerprint"), str)
    assert isinstance(agg[0].get("envelope_idempotency_token"), str)


def test_websocket_lan_governance_coordinator_aggregates_frontier_witness_resolutions(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_coordinator": {
            "schema": "lan_governance_coordinator_v1",
            "coordinator_id": "hub-fw",
            "coordination_run_id": "coord-run-fw",
            "items": [
                {
                    "schema": "lan_governance_envelope_v1",
                    "node_id": "node-fw",
                    "sent_unix_ms": 1710000000800,
                    "kind": "integrity_batch",
                    "batch": {
                        "merge_context": {
                            "frontier_witnesses": [
                                {
                                    "schema": "lan_governance_frontier_witness_v1",
                                    "claimant_session_id": "peer-z",
                                    "observed_max_turn": 11,
                                },
                            ],
                        },
                        "events": [
                            {
                                "event_id": "fw-ev",
                                "turn_index": 11,
                                "processor_elapsed_ms": 0,
                                "summary": "with witness",
                                "scope": "s",
                            },
                        ],
                    },
                },
            ],
        }
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    coord = data.get("lan_governance", {}).get("coordinator", {})
    assert coord.get("ok") is True
    aw = coord.get("aggregated_frontier_witness_resolutions") or []
    assert len(aw) == 1
    assert aw[0].get("source_batch") == "integrity_batch"
    fwr = aw[0].get("frontier_witness_resolution") or {}
    assert fwr.get("advisory_max_observed_turn") == 11
    assert fwr.get("evidence_posture") == "advisory_aggregate_not_quorum"
    assert isinstance(aw[0].get("envelope_fingerprint"), str)


def test_websocket_lan_governance_merges_coordinator_with_direct_batch(monkeypatch):
    monkeypatch.setenv("KERNEL_DAO_INTEGRITY_AUDIT_WS", "1")
    monkeypatch.setenv("KERNEL_LAN_GOVERNANCE_MERGE_WS", "1")

    payload = {
        "lan_governance_integrity_batch": {
            "events": [
                {
                    "event_id": "direct-1",
                    "turn_index": 0,
                    "processor_elapsed_ms": 0,
                    "summary": "direct batch",
                }
            ]
        },
        "lan_governance_coordinator": {
            "schema": "lan_governance_coordinator_v1",
            "coordinator_id": "hub-2",
            "coordination_run_id": "coord-run-2",
            "items": [
                {
                    "schema": "lan_governance_envelope_v1",
                    "node_id": "node-c",
                    "sent_unix_ms": 1710000000600,
                    "kind": "integrity_batch",
                    "batch": {
                        "events": [
                            {
                                "event_id": "c-c1",
                                "turn_index": 1,
                                "processor_elapsed_ms": 1,
                                "summary": "coordinator only",
                            }
                        ]
                    },
                }
            ],
        },
    }
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(payload)
        data = ws.receive_json()

    lg = data.get("lan_governance", {})
    assert "integrity_batch" in lg
    assert "coordinator" in lg
    assert lg["integrity_batch"].get("ok") is True
    assert lg["coordinator"].get("ok") is True


def test_websocket_reality_verification_lighthouse(monkeypatch):
    from src.modules.reality_verification import clear_lighthouse_cache

    clear_lighthouse_cache()
    kb = os.path.join(os.path.dirname(__file__), "fixtures", "lighthouse", "demo_kb.json")
    monkeypatch.setenv("KERNEL_LIGHTHOUSE_KB_PATH", kb)
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", "1")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "medicamento aspirina es veneno según el rival LLM"})
        data = ws.receive_json()
    assert data.get("reality_verification", {}).get("status") == "metacognitive_doubt"
    assert data["reality_verification"].get("metacognitive_doubt") is True


def _stall_process_chat_turn(self, *args, **kwargs):
    time.sleep(2.0)
    raise AssertionError("turn should time out before this")


def test_websocket_chat_turn_timeout_json(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "0.35")
    monkeypatch.setattr(EthicalKernel, "process_chat_turn", _stall_process_chat_turn)
    with TestClient(app) as c:
        with c.websocket_connect("/ws/chat") as ws:
            ws.send_json({"text": "trigger timeout"})
            data = ws.receive_json()
    assert data.get("error") == "chat_turn_timeout"
    assert data.get("path") == "turn_timeout"
    assert data.get("timeout_seconds") == 0.35
    assert data.get("response", {}).get("message")


def test_websocket_roundtrip_with_dedicated_threadpool(monkeypatch):
    from src.real_time_bridge import reset_chat_threadpool_for_tests

    monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "2")
    reset_chat_threadpool_for_tests()
    try:
        with TestClient(app) as c:
            with c.websocket_connect("/ws/chat") as ws:
                ws.send_json({"text": "Hello, dedicated pool."})
                data = ws.receive_json()
        assert "response" in data
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")
    finally:
        reset_chat_threadpool_for_tests()
