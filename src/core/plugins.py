"""
Ethos Core — External Plugins (V2.73)

Lightweight tool execution layer.
The LLM signals intent via [PLUGIN: name(args)] tokens.
The ChatEngine intercepts, executes, and re-injects the result
into the STM before dispatching the next LLM turn.

Design rules:
- CPU plugins (Time, System) MUST complete in <50ms.
- I/O plugins (Web) MUST time out within 3s and provide a fallback.
- Plugins MUST return a single plain-text result string.
- No plugin has access to the SecureVault or memory.
- Zero external dependencies beyond stdlib + httpx (already installed).

Usage:
    registry = PluginRegistry()
    result = registry.execute("Time")       # sync: "Son las 14:32:05"
    result = registry.execute("Web", "temperatura CDMX")  # sync (blocks)
    # Preferred inside async context:
    result = await registry.execute_async("Web", "temperatura CDMX")
"""

from __future__ import annotations

import asyncio
import json
import logging
import platform
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod

_log = logging.getLogger(__name__)

# Pattern to detect [PLUGIN: name] or [PLUGIN: name(args)] anywhere in LLM output
PLUGIN_PATTERN = re.compile(r"\[PLUGIN:\s*(\w+)(?:\(([^)]*)\))?\]", re.IGNORECASE)

# Pattern for bare shorthand: [Time], [System], etc. (built dynamically per registry)
_SHORTHAND_BASE = r"\[({names})(?:\(([^)]*)\))?\]"


class Plugin(ABC):
    """Base class for all Ethos plugins."""

    name: str
    description: str

    @abstractmethod
    def execute(self, args: str = "") -> str:
        """Run the plugin and return a plain-text result. Must be <50ms."""


class TimePlugin(Plugin):
    """Returns the current local time and date."""

    name = "Time"
    description = "Returns the current local date and time."

    def execute(self, args: str = "") -> str:
        import datetime

        now = datetime.datetime.now()
        return (
            f"Son las {now.strftime('%H:%M:%S')} del {now.strftime('%A %d de %B de %Y')} "
            f"(hora local del sistema)."
        )


class SystemPlugin(Plugin):
    """Returns lightweight host system status."""

    name = "System"
    description = "Returns CPU/memory usage and system platform."

    def execute(self, args: str = "") -> str:
        try:
            import psutil  # optional dependency

            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            return (
                f"Sistema: {platform.system()} {platform.release()}. "
                f"CPU: {cpu:.0f}% | RAM: {mem.percent:.0f}% usada "
                f"({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)."
            )
        except ImportError:
            return (
                f"Sistema: {platform.system()} {platform.release()} "
                f"(psutil no instalado — métricas de CPU/RAM no disponibles)."
            )


class WeatherPlugin(Plugin):
    """
    Real-time weather using wttr.in (free, no API key, JSON response).
    Args: city name. Example: [PLUGIN: Weather(Ciudad de Mexico)]
    """

    name = "Weather"
    description = "Current weather conditions for any city."
    _TIMEOUT = 3.0

    def execute(self, args: str = "") -> str:
        city = args.strip() or "Ciudad de Mexico"
        encoded = urllib.parse.quote(city)
        # format=3 → "{city}: {icon} {temp}", format=j1 → JSON
        url = f"https://wttr.in/{encoded}?format=j1"
        fallback = f"https://wttr.in/{encoded}"
        try:
            req = urllib.request.urlopen(url, timeout=self._TIMEOUT)
            raw = req.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
            current = data["current_condition"][0]
            temp_c = current["temp_C"]
            feels_c = current["FeelsLikeC"]
            humidity = current["humidity"]
            desc = current["weatherDesc"][0]["value"]
            area = data["nearest_area"][0]["areaName"][0]["value"]
            country = data["nearest_area"][0]["country"][0]["value"]
            return (
                f"Clima en {area}, {country}: {desc}. "
                f"Temperatura: {temp_c}°C (se siente como {feels_c}°C). "
                f"Humedad: {humidity}%."
            )
        except Exception as exc:
            _log.warning("[Weather] %s: %s", city, exc)
            return f"No pude obtener el clima para '{city}'. Consulta en tiempo real: {fallback}"


class WebPlugin(Plugin):
    """
    Real-time web search via DuckDuckGo Instant Answer API.
    No API key required. Timeout: 3s. Fallback: search URL.
    """

    name = "Web"
    description = "Search the web for current information: weather, news, public data."
    _TIMEOUT = 3.0
    _API = "https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"

    def execute(self, args: str = "") -> str:
        query = args.strip()
        if not query:
            return "Por favor proporciona un término de búsqueda. Ejemplo: [PLUGIN: Web(temperatura CDMX)]"

        encoded = urllib.parse.quote(query)
        url = self._API.format(query=encoded)
        fallback_url = f"https://duckduckgo.com/?q={encoded}"

        try:
            req = urllib.request.urlopen(url, timeout=self._TIMEOUT)
            raw = req.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
        except urllib.error.URLError as exc:
            _log.warning("[Web] Network error: %s", exc)
            return f"No pude conectarme a la red. Puedes buscar manualmente: {fallback_url}"
        except Exception as exc:
            _log.warning("[Web] Unexpected error: %s", exc)
            return f"Error en la búsqueda. Intenta en: {fallback_url}"

        # Priority: direct Answer > Abstract > first RelatedTopic > fallback
        if data.get("Answer"):
            return str(data["Answer"])

        abstract = data.get("AbstractText", "").strip()
        if abstract:
            source = data.get("AbstractSource", "DuckDuckGo")
            return f"{abstract} (Fuente: {source})"

        topics = data.get("RelatedTopics", [])
        for topic in topics:
            if isinstance(topic, dict) and topic.get("Text"):
                return topic["Text"]

        return f"No encontré una respuesta directa para '{query}'. Puedes buscar en: {fallback_url}"


class PluginRegistry:
    """Central registry. Plugins are looked up by name (case-insensitive)."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        # Register built-ins
        for cls in (TimePlugin, SystemPlugin, WeatherPlugin, WebPlugin):
            instance = cls()
            self._plugins[instance.name.lower()] = instance

    def register(self, plugin: Plugin) -> None:
        """Add or override a plugin at runtime."""
        self._plugins[plugin.name.lower()] = plugin
        _log.info("[Plugins] Registered: %s", plugin.name)

    def _combined_pattern(self) -> re.Pattern:
        """Combined regex that matches both [PLUGIN: X] and bare shorthand [X]."""
        names = "|".join(re.escape(n) for n in self._plugins)
        shorthand = _SHORTHAND_BASE.format(names=names)
        combined = PLUGIN_PATTERN.pattern + "|" + shorthand
        return re.compile(combined, re.IGNORECASE)

    def has_plugin_call(self, text: str) -> bool:
        """Fast check: does this text contain any plugin invocation form?"""
        return bool(self._combined_pattern().search(text))

    def execute(self, name: str, args: str = "") -> str | None:
        """
        Run plugin by name. Returns result string or None if unknown.
        Execution is timed; warns if >50ms.
        """
        key = name.strip().lower()
        plugin = self._plugins.get(key)
        if not plugin:
            _log.warning("[Plugins] Unknown plugin requested: %s", name)
            return None
        t0 = time.perf_counter()
        try:
            result = plugin.execute(args)
        except Exception as exc:
            _log.error("[Plugins] %s raised: %s", name, exc)
            return f"Error ejecutando el plugin {name}: {exc}"
        elapsed = (time.perf_counter() - t0) * 1000
        budget = 3000 if name.lower() == "web" else 50
        if elapsed > budget:
            _log.warning("[Plugins] %s took %.1fms (>%dms budget)", name, elapsed, budget)
        else:
            _log.debug("[Plugins] %s → %.1fms", name, elapsed)
        return result

    async def execute_async(self, name: str, args: str = "") -> str | None:
        """
        Async-safe wrapper: runs blocking I/O plugins in a thread pool
        so they don't block the asyncio event loop.
        """
        return await asyncio.to_thread(self.execute, name, args)

    def list_available(self) -> list[str]:
        """Return a sorted list of registered plugin names."""
        return sorted(p.name for p in self._plugins.values())

    # Patterns for weather queries + regex to extract city name
    _WEATHER_TRIGGERS = re.compile(
        r"\b(temperatura|clima|tiempo|calor|fr[ií]o|lluev[ae]|weather|forecast|pron[oó]stico)\b"
        r".*?\b(en|de|para|in|at)\s+([\w\s]+?)(?:\?|$)",
        re.I,
    )
    _WEATHER_KEYWORD = re.compile(
        r"\b(temperatura|clima|tiempo\s+en|weather|pron[oó]stico)\b", re.I
    )

    def detect_weather_query(self, text: str) -> str | None:
        """
        If text is a weather query, return the city name to search.
        Returns None if not a weather question.
        """
        if not self._WEATHER_KEYWORD.search(text):
            return None
        match = self._WEATHER_TRIGGERS.search(text)
        if match:
            city = match.group(3).strip().rstrip("?. ")
            return city if city else text.strip()
        # Fallback: use whole query as city
        return text.strip()

    # Patterns that deterministically require real-time web data.
    # These bypass LLM tool-use and trigger proactive pre-injection.
    _WEB_TRIGGERS: list[re.Pattern] = [
        re.compile(
            r"\b(qui[eé]n\s+gan[oó]|campe[oó]n|copa\s+del\s+mundo|mundial|champions)\b", re.I
        ),
        re.compile(
            r"\b(precio\s+de|cotizaci[oó]n|d[oó]lar|euro\s+a|tipo\s+de\s+cambio|bolsa)\b", re.I
        ),
        re.compile(r"\b(resultado\s+(de|del?)|marcador|score\s+de)\b", re.I),
        re.compile(r"\b(noticias?\s+(de|sobre|del?)|[uú]ltima\s+noticia|breaking\s+news)\b", re.I),
        re.compile(
            r"\b(n[uú]mero\s+de\s+(tel[eé]fono|emergencia)|c[oó]mo\s+llegar|direcci[oó]n\s+de)\b",
            re.I,
        ),
        re.compile(
            r"\b(accede\s+(a|al?)|obt[eé]n|trae|busca)\s+(los\s+)?(n[uú]meros?|informaci[oó]n)\s+de\b",
            re.I,
        ),
        re.compile(r"\b(vuelos?|avi[oó]n|aerol[ií]nea)\b", re.I),
        re.compile(r"\b(boletos?|voletos?|entradas?|conciertos?|eventos?)\b", re.I),
    ]

    def detect_web_query(self, text: str) -> str | None:
        """
        Deterministically detect if query requires real-time web data (non-weather).
        Returns the text as search query, or None if no web search needed.
        """
        for pattern in self._WEB_TRIGGERS:
            if pattern.search(text):
                return text.strip()
        return None

    def parse_and_execute(self, text: str) -> tuple[str | None, str | None]:
        """
        Scan text for the first [PLUGIN: name(args)] OR bare [name] token.
        Returns (plugin_name, result) or (None, None) if not found.
        """
        pattern = self._combined_pattern()
        match = pattern.search(text)
        if not match:
            return None, None
        # Group layout: (PLUGIN: name, PLUGIN: args, shorthand name, shorthand args)
        name = match.group(1) or match.group(3)
        args = match.group(2) or match.group(4) or ""
        if not name:
            return None, None
        result = self.execute(name, args)
        return name, result
