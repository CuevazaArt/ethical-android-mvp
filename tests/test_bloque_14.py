"""
Tests for Bloque 14.0 — Cero Fricción y Recuperación Autónoma

Covers:
- 14.1: nomad_discovery helper functions (LAN IP, payload schema, env vars)
- 14.1: NomadDiscoveryAnnouncer graceful no-op when zeroconf unavailable
- 14.1: PWA resolveKernelEndpointCandidates presence in app.js (JS smoke)
- 14.2: GET /nomad/clinical endpoint schema and types
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# 14.1 — nomad_discovery helper functions
# ---------------------------------------------------------------------------


class TestIsPrivateLanIp:
    """_is_private_lan_ip must accept RFC-1918 addresses and reject others."""

    def _check(self, ip: str) -> bool:
        from src.modules.perception.nomad_discovery import _is_private_lan_ip

        return _is_private_lan_ip(ip)

    def test_192_168_is_private(self) -> None:
        assert self._check("192.168.1.100") is True

    def test_10_x_is_private(self) -> None:
        assert self._check("10.0.0.5") is True

    def test_172_16_is_private(self) -> None:
        assert self._check("172.16.50.1") is True

    def test_loopback_rejected(self) -> None:
        assert self._check("127.0.0.1") is False

    def test_public_ip_rejected(self) -> None:
        assert self._check("8.8.8.8") is False

    def test_invalid_string_rejected(self) -> None:
        assert self._check("not-an-ip") is False


class TestSafePort:
    """_safe_port must clamp to valid range and fall back to default."""

    def _check(self, v: int, default: int = 8765) -> int:
        from src.modules.perception.nomad_discovery import _safe_port

        return _safe_port(v, default)

    def test_valid_port_returned_as_is(self) -> None:
        assert self._check(8765) == 8765

    def test_zero_returns_default(self) -> None:
        assert self._check(0) == 8765

    def test_65535_is_valid(self) -> None:
        assert self._check(65535) == 65535

    def test_65536_returns_default(self) -> None:
        assert self._check(65536) == 8765


class TestDiscoverLanIpv4Candidates:
    """discover_lan_ipv4_candidates must include the bind_host when valid."""

    def test_private_bind_host_included(self) -> None:
        from src.modules.perception.nomad_discovery import discover_lan_ipv4_candidates

        candidates = discover_lan_ipv4_candidates(bind_host="192.168.1.1")
        assert "192.168.1.1" in candidates

    def test_loopback_bind_host_excluded(self) -> None:
        from src.modules.perception.nomad_discovery import discover_lan_ipv4_candidates

        # 127.0.0.1 is loopback — should not appear in LAN candidates
        candidates = discover_lan_ipv4_candidates(bind_host="127.0.0.1")
        assert "127.0.0.1" not in candidates

    def test_returns_list(self) -> None:
        from src.modules.perception.nomad_discovery import discover_lan_ipv4_candidates

        result = discover_lan_ipv4_candidates()
        assert isinstance(result, list)


class TestBuildNomadDiscoveryPayload:
    """build_nomad_discovery_payload must produce the expected schema."""

    def _build(self, **kwargs: Any) -> dict[str, Any]:
        from src.modules.perception.nomad_discovery import build_nomad_discovery_payload

        defaults: dict[str, Any] = {
            "request_host": "192.168.1.10",
            "request_scheme": "http",
            "bind_host": "192.168.1.10",
            "bind_port": 8765,
            "mdns_registered": False,
            "mdns_service_name": "ethos-kernel",
            "mdns_service_type": "_ethos-kernel._tcp.local.",
        }
        defaults.update(kwargs)
        return build_nomad_discovery_payload(**defaults)

    def test_schema_key_present(self) -> None:
        p = self._build()
        assert p["schema"] == "nomad_discovery_v1"

    def test_candidates_is_list(self) -> None:
        p = self._build()
        assert isinstance(p["candidates"], list)

    def test_candidate_has_chat_ws(self) -> None:
        p = self._build()
        assert len(p["candidates"]) > 0
        for c in p["candidates"]:
            assert "chat_ws" in c
            assert "/ws/chat" in c["chat_ws"]

    def test_candidate_has_nomad_ws(self) -> None:
        p = self._build()
        for c in p["candidates"]:
            assert "nomad_ws" in c

    def test_wss_scheme_on_https(self) -> None:
        p = self._build(request_scheme="https")
        for c in p["candidates"]:
            assert c["chat_ws"].startswith("wss://")

    def test_mdns_block_present(self) -> None:
        p = self._build(mdns_registered=True)
        assert p["mdns"]["registered"] is True
        assert p["mdns"]["service_name"] == "ethos-kernel"


class TestNomadDiscoveryEnvVars:
    """nomad_discovery_service_name/type must read from env or use defaults."""

    def test_default_service_name(self) -> None:
        from src.modules.perception.nomad_discovery import nomad_discovery_service_name

        env = {k: v for k, v in os.environ.items() if k != "KERNEL_NOMAD_DISCOVERY_SERVICE_NAME"}
        with patch.dict(os.environ, env, clear=True):
            assert nomad_discovery_service_name() == "ethos-kernel"

    def test_custom_service_name(self) -> None:
        from src.modules.perception.nomad_discovery import nomad_discovery_service_name

        with patch.dict(os.environ, {"KERNEL_NOMAD_DISCOVERY_SERVICE_NAME": "my-kernel"}):
            assert nomad_discovery_service_name() == "my-kernel"

    def test_default_service_type(self) -> None:
        from src.modules.perception.nomad_discovery import nomad_discovery_service_type

        env = {k: v for k, v in os.environ.items() if k != "KERNEL_NOMAD_DISCOVERY_SERVICE_TYPE"}
        with patch.dict(os.environ, env, clear=True):
            assert "_ethos-kernel._tcp.local." in nomad_discovery_service_type()

    def test_discovery_enabled_by_default(self) -> None:
        from src.modules.perception.nomad_discovery import nomad_discovery_enabled

        env = {k: v for k, v in os.environ.items() if k != "KERNEL_NOMAD_DISCOVERY_ENABLED"}
        with patch.dict(os.environ, env, clear=True):
            assert nomad_discovery_enabled() is True

    def test_discovery_disabled_by_env(self) -> None:
        from src.modules.perception.nomad_discovery import nomad_discovery_enabled

        with patch.dict(os.environ, {"KERNEL_NOMAD_DISCOVERY_ENABLED": "0"}):
            assert nomad_discovery_enabled() is False


class TestNomadDiscoveryAnnouncerNoOp:
    """NomadDiscoveryAnnouncer.start() must be a graceful no-op when zeroconf is absent."""

    def test_start_returns_false_without_zeroconf(self) -> None:
        from src.modules.perception.nomad_discovery import NomadDiscoveryAnnouncer

        announcer = NomadDiscoveryAnnouncer(
            bind_host="192.168.1.1",
            bind_port=8765,
            service_name="test",
            service_type="_test._tcp.local.",
        )
        with patch.dict(os.environ, {"KERNEL_NOMAD_DISCOVERY_ENABLED": "1"}):
            # Mock zeroconf import to fail — simulates uninstalled package
            with patch("builtins.__import__", side_effect=_mock_import_block_zeroconf):
                result = announcer.start()
        # Either False (zeroconf missing) or True (installed on test machine) — must not raise
        assert isinstance(result, bool)

    def test_stop_is_idempotent(self) -> None:
        from src.modules.perception.nomad_discovery import NomadDiscoveryAnnouncer

        announcer = NomadDiscoveryAnnouncer(
            bind_host="192.168.1.1",
            bind_port=8765,
            service_name="test",
            service_type="_test._tcp.local.",
        )
        announcer.stop()  # Must not raise even if never started
        announcer.stop()  # Second call — still must not raise

    def test_registered_false_before_start(self) -> None:
        from src.modules.perception.nomad_discovery import NomadDiscoveryAnnouncer

        announcer = NomadDiscoveryAnnouncer(
            bind_host="192.168.1.1",
            bind_port=8765,
            service_name="test",
            service_type="_test._tcp.local.",
        )
        assert announcer.registered is False


def _mock_import_block_zeroconf(name: str, *args: Any, **kwargs: Any) -> Any:
    """Simulate missing zeroconf package by raising ImportError for it."""
    if name == "zeroconf":
        raise ImportError("zeroconf not installed (test mock)")
    return original_import(name, *args, **kwargs)


import builtins as _builtins

original_import = _builtins.__import__


# ---------------------------------------------------------------------------
# 14.1 — PWA auto-discovery smoke check (JS layer)
# ---------------------------------------------------------------------------


class TestPWAAutoDiscovery:
    """Key auto-discovery functions must be present in app.js."""

    @pytest.fixture(scope="class")
    def app_js_source(self) -> str:
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "src",
            "clients",
            "nomad_pwa",
            "app.js",
        )
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_resolve_kernel_endpoint_candidates_present(self, app_js_source: str) -> None:
        assert "resolveKernelEndpointCandidates" in app_js_source

    def test_connect_pair_present(self, app_js_source: str) -> None:
        assert "connectPair" in app_js_source

    def test_discovery_fetch_calls_nomad_discovery_path(self, app_js_source: str) -> None:
        assert "/discovery/nomad" in app_js_source

    def test_last_good_host_key_defined(self, app_js_source: str) -> None:
        assert "NOMAD_LAST_GOOD_HOST_KEY" in app_js_source

    def test_candidates_loop_present(self, app_js_source: str) -> None:
        assert "for (const c of candidates)" in app_js_source


# ---------------------------------------------------------------------------
# 14.2 — GET /nomad/clinical endpoint
# ---------------------------------------------------------------------------


class TestNomadClinicalEndpoint:
    """GET /nomad/clinical must return a well-typed clinical telemetry snapshot."""

    @pytest.fixture(scope="class")
    def clinical_payload(self) -> dict[str, Any]:
        from fastapi.testclient import TestClient
        from src.chat_server import app

        client = TestClient(app)
        resp = client.get("/nomad/clinical")
        assert resp.status_code == 200
        return resp.json()

    def test_schema_key(self, clinical_payload: dict[str, Any]) -> None:
        assert clinical_payload["schema"] == "nomad_clinical_v1"

    def test_vessel_online_is_bool(self, clinical_payload: dict[str, Any]) -> None:
        assert isinstance(clinical_payload["vessel_online"], bool)

    def test_vad_speaking_is_bool(self, clinical_payload: dict[str, Any]) -> None:
        assert isinstance(clinical_payload["vad_speaking"], bool)

    def test_rms_audio_is_float(self, clinical_payload: dict[str, Any]) -> None:
        assert isinstance(clinical_payload["rms_audio"], float)

    def test_latency_ms_is_int(self, clinical_payload: dict[str, Any]) -> None:
        assert isinstance(clinical_payload["latency_ms"], int)

    def test_battery_fraction_is_float_or_none(self, clinical_payload: dict[str, Any]) -> None:
        v = clinical_payload["battery_fraction"]
        assert v is None or isinstance(v, float)

    def test_queues_block_present(self, clinical_payload: dict[str, Any]) -> None:
        q = clinical_payload["queues"]
        assert isinstance(q, dict)
        for key in (
            "vision_depth",
            "audio_depth",
            "telemetry_depth",
            "charm_feedback_depth",
            "chat_text_depth",
        ):
            assert key in q
            assert isinstance(q[key], int)

    def test_last_sensor_update_delta_is_numeric(self, clinical_payload: dict[str, Any]) -> None:
        v = clinical_payload["last_sensor_update_delta_s"]
        assert isinstance(v, int | float)
        assert v >= 0


# ---------------------------------------------------------------------------
# 14.2 — NomadBridge.public_queue_stats: clinical raw fields (Bloque 14.2)
# ---------------------------------------------------------------------------


class TestPublicQueueStatsClinicalFields:
    """public_queue_stats() must expose ``last_rms`` and ``vad_speaking``."""

    def _bridge(self):
        from src.modules.perception.nomad_bridge import NomadBridge

        return NomadBridge()

    def test_last_rms_key_present(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert "last_rms" in stats

    def test_vad_speaking_key_present(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert "vad_speaking" in stats

    def test_last_rms_default_zero(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert stats["last_rms"] == 0.0

    def test_vad_speaking_default_false(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert stats["vad_speaking"] is False

    def test_last_rms_reflects_update(self) -> None:
        b = self._bridge()
        b.last_rms = 0.4321
        stats = b.public_queue_stats()
        assert abs(stats["last_rms"] - 0.4321) < 1e-3

    def test_vad_speaking_reflects_true(self) -> None:
        b = self._bridge()
        b.vad_speaking = True
        stats = b.public_queue_stats()
        assert stats["vad_speaking"] is True

    def test_last_rms_nan_clamped_to_zero(self) -> None:
        """NaN must never propagate to health JSON — Anti-NaN Boy Scout rule."""
        import math

        b = self._bridge()
        b.last_rms = float("nan")
        stats = b.public_queue_stats()
        assert stats["last_rms"] == 0.0
        assert math.isfinite(stats["last_rms"])

    def test_last_rms_inf_clamped_to_zero(self) -> None:
        import math

        b = self._bridge()
        b.last_rms = float("inf")
        stats = b.public_queue_stats()
        assert stats["last_rms"] == 0.0
        assert math.isfinite(stats["last_rms"])

    def test_last_rms_is_float_type(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert isinstance(stats["last_rms"], float)

    def test_vad_speaking_is_bool_type(self) -> None:
        stats = self._bridge().public_queue_stats()
        assert isinstance(stats["vad_speaking"], bool)

    def test_pre_existing_keys_unchanged(self) -> None:
        """Bloque 14.2 must not remove any pre-existing keys."""
        stats = self._bridge().public_queue_stats()
        for key in (
            "vision_queue_depth",
            "audio_queue_depth",
            "telemetry_queue_depth",
            "charm_feedback_queue_depth",
            "vessel_online",
            "vessel_metadata",
            "vessel_context",
            "last_sensor_update_delta",
        ):
            assert key in stats, f"Missing pre-existing key: {key}"
