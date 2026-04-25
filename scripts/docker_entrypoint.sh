#!/usr/bin/env bash
# scripts/docker_entrypoint.sh — Ethos Kernel GPU container entrypoint.
#
# 1. Detects the container's IP for the TLS certificate SAN.
# 2. Generates a self-signed cert (idempotent via gen_cert.py).
# 3. Starts uvicorn with HTTPS on port 8443.
#
# Environment overrides:
#   ETHOS_CERT_IP   — Force a specific IP in the cert SAN (e.g. host LAN IP).
#   ETHOS_HTTP_ONLY — Set to "1" to skip TLS and serve plain HTTP on 8000.

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo " Ethos Kernel — GPU Container Startup"
echo "═══════════════════════════════════════════════════════════════"

# --- Resolve IP for certificate ---
if [ -n "${ETHOS_CERT_IP:-}" ]; then
    CERT_IP="$ETHOS_CERT_IP"
    echo "  Using forced cert IP: $CERT_IP"
else
    # Auto-detect container IP (first non-loopback IPv4)
    CERT_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "0.0.0.0")
    echo "  Auto-detected container IP: $CERT_IP"
fi

# --- HTTP-only mode (for reverse proxy setups) ---
if [ "${ETHOS_HTTP_ONLY:-0}" = "1" ]; then
    echo "  Mode: HTTP-only (no TLS)"
    echo "  Listening on: http://0.0.0.0:8000"
    echo "═══════════════════════════════════════════════════════════════"
    exec uvicorn src.server.app:app \
        --host 0.0.0.0 \
        --port 8000
fi

# --- Generate TLS certificate ---
echo "  Generating TLS certificate..."
python scripts/gen_cert.py --ip "$CERT_IP" --force

# --- Start HTTPS server ---
echo ""
echo "  Mode: HTTPS (TLS)"
echo "  Listening on: https://$CERT_IP:8443"
echo "  Mobile access: https://$CERT_IP:8443/nomad"
echo "═══════════════════════════════════════════════════════════════"
exec uvicorn src.server.app:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile certs/server.key \
    --ssl-certfile certs/server.crt
