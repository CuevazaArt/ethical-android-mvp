# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — MeshListener
V1.0: mDNS service discovery for Nomad Android parasites.

Listens for `_ethos._tcp.local.` services and maintains a live roster of
discovered Android nodes keyed by device_id.

Usage
-----
    listener = MeshListener()
    listener.start()          # non-blocking; runs in daemon thread
    ...
    roster = listener.roster  # dict[str, DiscoveryPayload]
    listener.stop()
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

_log = logging.getLogger(__name__)

# mDNS service type published by every Nomad Android node.
_SERVICE_TYPE = "_ethos._tcp.local."

# Regex that matches valid device_id values per DiscoveryPayload schema.
_DEVICE_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")


# ---------------------------------------------------------------------------
# Data model (mirrors DiscoveryPayload JSON Schema, mesh_protocol_v1.md)
# ---------------------------------------------------------------------------


@dataclass
class NodeCapabilities:
    """Hardware / software capabilities of a discovered node."""

    available_ram_mb: int = 0
    has_microphone: bool = False
    has_camera: bool = False
    slm_available: bool = False


@dataclass
class DiscoveryPayload:
    """Parsed representation of a Nomad mDNS TXT record."""

    protocol_version: str
    device_id: str
    ip: str
    port: int
    capabilities: NodeCapabilities
    # Internal bookkeeping — not part of the wire protocol.
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    def summary(self) -> str:
        caps = self.capabilities
        return (
            f"device_id={self.device_id!r} ip={self.ip} port={self.port} "
            f"ram={caps.available_ram_mb}MB mic={caps.has_microphone} "
            f"cam={caps.has_camera} slm={caps.slm_available}"
        )


# ---------------------------------------------------------------------------
# TXT record parsing helpers
# ---------------------------------------------------------------------------


def _decode_txt(properties: dict[bytes, Any]) -> dict[str, str]:
    """Decode zeroconf TXT record byte keys/values to plain strings."""
    result: dict[str, str] = {}
    for k, v in properties.items():
        key = k.decode("utf-8") if isinstance(k, bytes) else str(k)
        if isinstance(v, bytes):
            value = v.decode("utf-8")
        elif v is None:
            value = ""
        else:
            value = str(v)
        result[key] = value
    return result


def _parse_capabilities(raw: str | None) -> NodeCapabilities:
    """Parse the `capabilities` TXT field (JSON string or individual fields)."""
    if not raw:
        return NodeCapabilities()
    try:
        data: dict[str, Any] = json.loads(raw)
        return NodeCapabilities(
            available_ram_mb=int(data.get("available_ram_mb", 0)),
            has_microphone=bool(data.get("has_microphone", False)),
            has_camera=bool(data.get("has_camera", False)),
            slm_available=bool(data.get("slm_available", False)),
        )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        _log.warning("MeshListener: could not parse capabilities TXT: %s — %s", raw, exc)
        return NodeCapabilities()


def _parse_txt_to_payload(
    txt: dict[str, str],
    ip: str,
    port: int,
) -> DiscoveryPayload | None:
    """
    Convert a decoded TXT dict + connection info into a DiscoveryPayload.

    Returns None if required fields are missing or invalid.
    """
    device_id = txt.get("device_id", "").strip()
    if not _DEVICE_ID_RE.match(device_id):
        _log.warning(
            "MeshListener: invalid or missing device_id %r in TXT record — skipping node",
            device_id,
        )
        return None

    protocol_version = txt.get("protocol_version", "").strip()
    if not protocol_version:
        _log.warning(
            "MeshListener: missing protocol_version for device %r — skipping",
            device_id,
        )
        return None

    # Accept the major version "1" family; future majors would need a migration path.
    major = protocol_version.split(".")[0]
    if major != "1":
        _log.warning(
            "MeshListener: unsupported protocol major version %r for device %r — skipping",
            major,
            device_id,
        )
        return None

    capabilities = _parse_capabilities(txt.get("capabilities"))

    return DiscoveryPayload(
        protocol_version=protocol_version,
        device_id=device_id,
        ip=ip,
        port=port,
        capabilities=capabilities,
    )


# ---------------------------------------------------------------------------
# Zeroconf service listener
# ---------------------------------------------------------------------------


class _ZeroconfHandler(ServiceListener):
    """
    Zeroconf callback adapter.

    Zeroconf calls these methods from its own internal thread, so all roster
    mutations are protected by ``_lock``.
    """

    def __init__(self, roster: dict[str, DiscoveryPayload], lock: threading.Lock) -> None:
        self._roster = roster
        self._lock = lock

    # ------------------------------------------------------------------ #
    # ServiceListener interface                                            #
    # ------------------------------------------------------------------ #

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self._upsert_service(zc, type_, name, event="add")

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self._upsert_service(zc, type_, name, event="update")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        # Identify the roster entry by service name — device_id lives in TXT,
        # but we store the service name → device_id mapping internally.
        with self._lock:
            # Linear scan; roster is small (O(N) is fine).
            victim_id: str | None = None
            for dev_id, payload in self._roster.items():
                # Service names are formatted as "<device_id>._ethos._tcp.local."
                if name.startswith(dev_id):
                    victim_id = dev_id
                    break

            if victim_id:
                removed = self._roster.pop(victim_id)
                _log.info(
                    "MeshListener: node removed from roster — %s",
                    removed.summary(),
                )
            else:
                _log.debug(
                    "MeshListener: remove_service called for unknown service %r — ignoring",
                    name,
                )

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _upsert_service(self, zc: Zeroconf, type_: str, name: str, event: str) -> None:
        info = zc.get_service_info(type_, name)
        if info is None:
            _log.debug("MeshListener: could not retrieve service info for %r", name)
            return

        # zeroconf returns a list of IPv4 addresses; pick the first valid one.
        addresses = info.parsed_scoped_addresses()
        if not addresses:
            _log.warning("MeshListener: service %r has no addresses — skipping", name)
            return
        ip = addresses[0]
        port = info.port or 0

        txt = _decode_txt(info.properties)
        payload = _parse_txt_to_payload(txt, ip, port)
        if payload is None:
            return

        with self._lock:
            existing = self._roster.get(payload.device_id)
            if existing is not None:
                # Update in-place; preserve first_seen.
                payload.first_seen = existing.first_seen
            self._roster[payload.device_id] = payload

        _log.info(
            "MeshListener: node %s [%s] — %s",
            event,
            payload.device_id,
            payload.summary(),
        )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


class MeshListener:
    """
    Non-blocking mDNS listener for Nomad Android nodes.

    Thread-safety
    -------------
    ``roster`` is a live dict protected by an internal ``threading.Lock``.
    Read access via :py:meth:`snapshot` returns a consistent copy without
    holding the lock for the caller's entire operation.

    Example
    -------
    ::

        listener = MeshListener()
        listener.start()
        # ... application runs ...
        for node in listener.snapshot().values():
            print(node.summary())
        listener.stop()
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        # Live roster: device_id → DiscoveryPayload
        self._roster: dict[str, DiscoveryPayload] = {}
        self._zeroconf: Zeroconf | None = None
        self._browser: ServiceBrowser | None = None
        self._started = False

    # ------------------------------------------------------------------ #
    # Public properties                                                    #
    # ------------------------------------------------------------------ #

    @property
    def roster(self) -> dict[str, DiscoveryPayload]:
        """
        Direct reference to the live roster dict.

        **Warning:** mutations from zeroconf's thread are protected by the
        internal lock, but callers iterating this dict outside the lock
        may see partial updates. Prefer :py:meth:`snapshot` for safe reads.
        """
        return self._roster

    def snapshot(self) -> dict[str, DiscoveryPayload]:
        """Return a shallow copy of the roster under lock — safe for iteration."""
        with self._lock:
            return dict(self._roster)

    def is_running(self) -> bool:
        return self._started

    # ------------------------------------------------------------------ #
    # Lifecycle                                                            #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """
        Start listening for `_ethos._tcp.local.` services.

        Non-blocking — zeroconf runs its own daemon threads internally.
        Safe to call from any thread, including asyncio event loops
        (the zeroconf I/O does NOT run on the event loop).

        Raises
        ------
        RuntimeError
            If ``start()`` is called on an already-running listener.
        """
        if self._started:
            raise RuntimeError("MeshListener is already running. Call stop() first.")

        _log.info("MeshListener: starting — listening for %s", _SERVICE_TYPE)
        self._zeroconf = Zeroconf()
        handler = _ZeroconfHandler(self._roster, self._lock)
        self._browser = ServiceBrowser(self._zeroconf, _SERVICE_TYPE, handler)
        self._started = True
        _log.info("MeshListener: active.")

    def stop(self) -> None:
        """
        Gracefully close the mDNS listener and clear the roster.

        Idempotent — safe to call multiple times.
        """
        if not self._started:
            return

        _log.info("MeshListener: stopping...")
        try:
            if self._zeroconf is not None:
                self._zeroconf.close()
        except Exception as exc:  # pragma: no cover
            _log.warning("MeshListener: error during zeroconf close: %s", exc)
        finally:
            self._zeroconf = None
            self._browser = None
            self._started = False
            with self._lock:
                self._roster.clear()
        _log.info("MeshListener: stopped. Roster cleared.")

    def __enter__(self) -> "MeshListener":
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()
