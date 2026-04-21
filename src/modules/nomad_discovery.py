from __future__ import annotations

import ipaddress
import logging
import os
import socket
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _safe_port(v: int, default: int = 8765) -> int:
    if 1 <= int(v) <= 65535:
        return int(v)
    return default


def _is_private_lan_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return bool(ip.version == 4 and ip.is_private and not ip.is_loopback)


def discover_lan_ipv4_candidates(bind_host: str | None = None) -> list[str]:
    """Best-effort LAN IP discovery for operator UX and Nomad bootstrapping."""
    out: list[str] = []

    def _add(ip: str | None) -> None:
        if not ip:
            return
        if _is_private_lan_ip(ip) and ip not in out:
            out.append(ip)

    if bind_host:
        _add(bind_host)

    try:
        host_name = socket.gethostname()
        for row in socket.getaddrinfo(host_name, None, family=socket.AF_INET, type=socket.SOCK_STREAM):
            _add(str(row[4][0]))
    except OSError:
        pass

    # UDP connect trick: no packets need to be sent; obtains preferred outbound local IP.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            _add(str(s.getsockname()[0]))
    except OSError:
        pass

    return out


def build_nomad_discovery_payload(
    *,
    request_host: str,
    request_scheme: str,
    bind_host: str,
    bind_port: int,
    mdns_registered: bool,
    mdns_service_name: str,
    mdns_service_type: str,
) -> dict[str, Any]:
    """Public payload for HTTP discovery endpoint consumed by Nomad PWA."""
    port = _safe_port(bind_port)
    ws_scheme = "wss" if str(request_scheme).lower() == "https" else "ws"
    http_scheme = "https" if ws_scheme == "wss" else "http"

    candidates: list[str] = []
    if request_host and request_host not in candidates:
        candidates.append(request_host)
    for ip in discover_lan_ipv4_candidates(bind_host):
        if ip not in candidates:
            candidates.append(ip)

    endpoints: list[dict[str, str]] = []
    for host in candidates:
        base = f"{ws_scheme}://{host}:{port}"
        endpoints.append(
            {
                "host": host,
                "chat_ws": f"{base}/ws/chat",
                "nomad_ws": f"{base}/ws/nomad",
                "dashboard_ws": f"{base}/ws/dashboard",
                "nomad_ui": f"{http_scheme}://{host}:{port}/nomad/",
            }
        )

    return {
        "schema": "nomad_discovery_v1",
        "service": "ethos-kernel-chat",
        "mdns": {
            "enabled": nomad_discovery_enabled(),
            "registered": mdns_registered,
            "service_name": mdns_service_name,
            "service_type": mdns_service_type,
        },
        "bind": {"host": bind_host, "port": port},
        "candidates": endpoints,
    }


def nomad_discovery_enabled() -> bool:
    return _env_truthy("KERNEL_NOMAD_DISCOVERY_ENABLED", default=True)


def nomad_discovery_service_name() -> str:
    raw = os.environ.get("KERNEL_NOMAD_DISCOVERY_SERVICE_NAME", "ethos-kernel").strip()
    return raw or "ethos-kernel"


def nomad_discovery_service_type() -> str:
    raw = os.environ.get("KERNEL_NOMAD_DISCOVERY_SERVICE_TYPE", "_ethos-kernel._tcp.local.").strip()
    return raw or "_ethos-kernel._tcp.local."


@dataclass(slots=True)
class NomadDiscoveryAnnouncer:
    """Optional Zeroconf/mDNS advertisement. Safe no-op if package missing."""

    bind_host: str
    bind_port: int
    service_name: str
    service_type: str
    _zc: Any = None
    _info: Any = None
    _registered: bool = False

    @property
    def registered(self) -> bool:
        return self._registered

    def start(self) -> bool:
        if not nomad_discovery_enabled():
            self._registered = False
            return False
        try:
            from zeroconf import ServiceInfo, Zeroconf  # type: ignore
        except Exception:
            logger.info("Nomad discovery: python-zeroconf not installed; mDNS disabled.")
            self._registered = False
            return False

        ips = discover_lan_ipv4_candidates(self.bind_host)
        if not ips:
            logger.warning("Nomad discovery: no private LAN IP found, mDNS skipped.")
            self._registered = False
            return False

        try:
            addresses = [socket.inet_aton(ip) for ip in ips]
            server_host = f"{self.service_name}.local."
            self._info = ServiceInfo(
                type_=self.service_type,
                name=f"{self.service_name}.{self.service_type}",
                addresses=addresses,
                port=_safe_port(self.bind_port),
                properties={
                    b"service": b"ethos-kernel-chat",
                    b"path": b"/discovery/nomad",
                    b"ws": b"/ws/chat",
                },
                server=server_host,
            )
            self._zc = Zeroconf()
            self._zc.register_service(self._info)
            self._registered = True
            logger.info(
                "Nomad discovery mDNS registered service=%s type=%s ips=%s port=%d",
                self.service_name,
                self.service_type,
                ",".join(ips),
                _safe_port(self.bind_port),
            )
            return True
        except Exception as e:
            logger.warning("Nomad discovery mDNS registration failed: %s", e)
            self._registered = False
            self.stop()
            return False

    def stop(self) -> None:
        try:
            if self._zc is not None and self._info is not None and self._registered:
                self._zc.unregister_service(self._info)
        except Exception:
            pass
        finally:
            try:
                if self._zc is not None:
                    self._zc.close()
            except Exception:
                pass
            self._zc = None
            self._info = None
            self._registered = False
