#!/usr/bin/env bash
# Start chat server on 0.0.0.0 for LAN (smartphone thin client on same WiFi).
# Usage: ./scripts/start_lan_server.sh [PORT]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export CHAT_HOST="0.0.0.0"
export CHAT_PORT="${1:-8765}"
echo "CHAT_HOST=$CHAT_HOST CHAT_PORT=$CHAT_PORT"
echo "Health: http://127.0.0.1:${CHAT_PORT}/health"
if command -v ip >/dev/null 2>&1; then
  echo "LAN hints (ip route get 1.1.1.1 may show src IP):"
  ip -4 addr show scope global 2>/dev/null | awk '/inet / {print $2}' || true
fi
PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then PY="python3"; fi
exec "$PY" -m src.runtime
