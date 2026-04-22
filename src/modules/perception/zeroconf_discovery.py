# Status: SCAFFOLD
import logging
import os
import socket

_log = logging.getLogger(__name__)


class ZeroconfAdvertiser:
    """
    Bloque 14.1: Auto-Descubrimiento (mDNS/Zeroconf).
    Advertises the Ethos Kernel service on the local network so that Nomad Vessels
    (Smartphones) can discover the PC's IP automatically.
    """

    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.zeroconf = None
        self.info = None

    def start(self):
        try:
            # Task 14.1 requires 'zeroconf' package
            from zeroconf import IPVersion, ServiceInfo, Zeroconf

            _log.info("Zeroconf: Starting mDNS advertisement...")

            self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)

            # Robust Local IP detection for multi-interface setups
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Target a non-routable address to force routing table lookup
                s.connect(("10.255.255.255", 1))
                local_ip = s.getsockname()[0]
            except Exception:
                local_ip = "127.0.0.1"
            finally:
                s.close()

            desc = {
                "path": "/nomad/",
                "version": "1.0",
                "node_id": os.environ.get("KERNEL_NODE_ID", "ethos-primary"),
            }

            # _ethos-kernel._tcp.local. service type
            self.info = ServiceInfo(
                "_ethos-kernel._tcp.local.",
                f"{self.name}._ethos-kernel._tcp.local.",
                addresses=[socket.inet_aton(local_ip)],
                port=self.port,
                properties=desc,
                server=f"{socket.gethostname()}.local.",
            )

            self.zeroconf.register_service(self.info)
            _log.info(f"Zeroconf: Service registered as {self.name} on {local_ip}:{self.port}")

        except ImportError:
            _log.warning(
                "Zeroconf: Library NOT found. Task 14.1 inactive. Run 'pip install zeroconf' to enable mDNS."
            )
        except Exception as e:
            _log.error(f"Zeroconf: Failed to start advertisement: {e}")

    def stop(self):
        try:
            if self.zeroconf:
                if self.info:
                    self.zeroconf.unregister_service(self.info)
                self.zeroconf.close()
                self.zeroconf = None
                _log.info("Zeroconf: Service stopped.")
        except Exception as e:
            _log.debug(f"Zeroconf: Suppression error during shutdown: {e}")


_ADVERTISER: ZeroconfAdvertiser | None = None


def start_zeroconf_broadcast(port: int, name: str | None = None):
    global _ADVERTISER
    if _ADVERTISER is None:
        service_name = name or os.environ.get("KERNEL_MDNS_NAME", "EthosKernel")
        _ADVERTISER = ZeroconfAdvertiser(service_name, port)
        _ADVERTISER.start()


def stop_zeroconf_broadcast():
    global _ADVERTISER
    if _ADVERTISER:
        _ADVERTISER.stop()
        _ADVERTISER = None
