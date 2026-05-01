"""
Tests — Plugins V2.73

Unit tests for PluginRegistry, TimePlugin, SystemPlugin, WebPlugin
and the pattern parser.
"""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

from src.core.plugins import (
    PLUGIN_PATTERN,
    Plugin,
    PluginRegistry,
    SystemPlugin,
    TimePlugin,
    WebPlugin,
)

# ── TimePlugin ────────────────────────────────────────────────────────────────


class TestTimePlugin:
    def setup_method(self):
        self.plugin = TimePlugin()

    def test_name(self):
        assert self.plugin.name == "Time"

    def test_execute_returns_string(self):
        result = self.plugin.execute()
        assert isinstance(result, str)
        assert len(result) > 10

    def test_execute_contains_time_pattern(self):
        result = self.plugin.execute()
        # Should contain two-digit hours like "14:32:05"
        assert re.search(r"\d{2}:\d{2}:\d{2}", result), f"No time in: {result}"

    def test_execute_contains_date(self):
        result = self.plugin.execute()
        # Should contain a 4-digit year like 2026
        assert re.search(r"\b20\d{2}\b", result), f"No year in: {result}"

    def test_execute_fast(self):
        import time

        t0 = time.perf_counter()
        self.plugin.execute()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 50, f"TimePlugin too slow: {elapsed_ms:.1f}ms"


# ── SystemPlugin ──────────────────────────────────────────────────────────────


class TestSystemPlugin:
    def setup_method(self):
        self.plugin = SystemPlugin()

    def test_name(self):
        assert self.plugin.name == "System"

    def test_execute_returns_string(self):
        result = self.plugin.execute()
        assert isinstance(result, str)
        assert len(result) > 5

    def test_execute_contains_platform(self):
        import platform

        result = self.plugin.execute()
        assert platform.system() in result

    def test_execute_fast(self):
        import time

        t0 = time.perf_counter()
        self.plugin.execute()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 50, f"SystemPlugin too slow: {elapsed_ms:.1f}ms"


# ── WebPlugin ─────────────────────────────────────────────────────────────────


class TestWebPlugin:
    def setup_method(self):
        self.plugin = WebPlugin()

    def test_name(self):
        assert self.plugin.name == "Web"

    def test_empty_query_returns_hint(self):
        result = self.plugin.execute("")
        assert "PLUGIN" in result or "búsqueda" in result.lower()

    def test_uses_direct_answer(self):
        mock_data = {"Answer": "42", "AbstractText": "", "RelatedTopics": []}
        with patch("urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = __import__("json").dumps(mock_data).encode()
            mock_open.return_value.__enter__ = lambda s: mock_resp
            mock_open.return_value.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp
            result = self.plugin.execute("ultimate answer")
        assert result == "42"

    def test_falls_back_to_abstract(self):
        mock_data = {
            "Answer": "",
            "AbstractText": "El Quijote es una novela de Cervantes.",
            "AbstractSource": "Wikipedia",
            "RelatedTopics": [],
        }
        with patch("urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = __import__("json").dumps(mock_data).encode()
            mock_open.return_value = mock_resp
            result = self.plugin.execute("Don Quijote")
        assert "Cervantes" in result
        assert "Wikipedia" in result

    def test_falls_back_to_url_on_network_error(self):
        import urllib.error

        with patch(
            "urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")
        ):
            result = self.plugin.execute("temperatura Guadalajara")
        assert "duckduckgo.com" in result
        assert result.startswith("No pude")

    def test_fallback_url_on_empty_response(self):
        mock_data = {"Answer": "", "AbstractText": "", "RelatedTopics": []}
        with patch("urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = __import__("json").dumps(mock_data).encode()
            mock_open.return_value = mock_resp
            result = self.plugin.execute("xyzzy_noresult_12345")
        assert "duckduckgo.com" in result


# ── PluginRegistry ────────────────────────────────────────────────────────────


class TestPluginRegistry:
    def setup_method(self):
        self.registry = PluginRegistry()

    def test_time_registered(self):
        assert "Time" in self.registry.list_available()

    def test_system_registered(self):
        assert "System" in self.registry.list_available()

    def test_web_registered(self):
        assert "Web" in self.registry.list_available()

    def test_list_sorted(self):
        names = self.registry.list_available()
        assert names == sorted(names)

    def test_execute_time(self):
        result = self.registry.execute("Time")
        assert result is not None
        assert len(result) > 5

    def test_execute_system(self):
        result = self.registry.execute("System")
        assert result is not None

    def test_execute_case_insensitive(self):
        r1 = self.registry.execute("TIME")
        r2 = self.registry.execute("time")
        r3 = self.registry.execute("Time")
        assert r1 and r2 and r3

    def test_execute_unknown_returns_none(self):
        result = self.registry.execute("NonExistentPlugin42")
        assert result is None

    def test_custom_plugin_registration(self):
        class EchoPlugin(Plugin):
            name = "Echo"
            description = "Echoes args"

            def execute(self, args: str = "") -> str:
                return f"Echo: {args}"

        self.registry.register(EchoPlugin())
        assert "Echo" in self.registry.list_available()
        assert self.registry.execute("Echo", "hello") == "Echo: hello"

    def test_has_plugin_call_web_shorthand(self):
        assert self.registry.has_plugin_call("[Web(consulta)]")

    def test_has_plugin_call_full_form(self):
        assert self.registry.has_plugin_call("[PLUGIN: Web(consulta)]")

    def test_has_plugin_call_no_match(self):
        assert not self.registry.has_plugin_call("Respuesta normal")


# ── Pattern Parser ────────────────────────────────────────────────────────────


class TestPluginPattern:
    def test_basic_match(self):
        text = "Para saber la hora usa [PLUGIN: Time]"
        m = PLUGIN_PATTERN.search(text)
        assert m is not None
        assert m.group(1) == "Time"

    def test_with_args(self):
        text = "[PLUGIN: Web(temperatura CDMX)]"
        m = PLUGIN_PATTERN.search(text)
        assert m is not None
        assert m.group(1) == "Web"
        assert m.group(2) == "temperatura CDMX"

    def test_case_insensitive(self):
        text = "[plugin: time]"
        m = PLUGIN_PATTERN.search(text)
        assert m is not None

    def test_no_match(self):
        text = "Respuesta normal sin plugins"
        m = PLUGIN_PATTERN.search(text)
        assert m is None

    def test_parse_and_execute_time(self):
        registry = PluginRegistry()
        name, result = registry.parse_and_execute("Aquí está la hora: [PLUGIN: Time]")
        assert name == "Time"
        assert result is not None

    def test_parse_and_execute_web_with_args(self):
        registry = PluginRegistry()
        mock_data = {"Answer": "22°C", "AbstractText": "", "RelatedTopics": []}
        with patch("urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = __import__("json").dumps(mock_data).encode()
            mock_open.return_value = mock_resp
            name, result = registry.parse_and_execute(
                "[PLUGIN: Web(temperatura Madrid)]"
            )
        assert name == "Web"
        assert result == "22°C"

    def test_parse_and_execute_no_match(self):
        registry = PluginRegistry()
        name, result = registry.parse_and_execute("Respuesta normal sin herramientas")
        assert name is None
        assert result is None
