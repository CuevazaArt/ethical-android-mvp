#!/usr/bin/env python3
"""
Simple WebSocket load generator for /ws/chat (asyncio + websockets).

Install (dev): pip install websockets
Usage:
  python scripts/loadtest/ws_stress.py --url ws://127.0.0.1:8765/ws/chat --clients 20 --messages 5

Does not assert SLOs; use for manual smoke / limit finding alongside Prometheus metrics.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from typing import Any

import websockets


async def one_client(uri: str, n_messages: int, payload: str) -> tuple[int, float]:
    """Return (successful_roundtrips, elapsed_seconds)."""
    t0 = time.perf_counter()
    ok = 0
    async with websockets.connect(uri, max_size=2**22) as ws:
        for _ in range(n_messages):
            await ws.send(json.dumps({"text": payload}))
            raw = await ws.recv()
            data: Any = json.loads(raw)
            if isinstance(data, dict) and ("response" in data or data.get("error")):
                ok += 1
    return ok, time.perf_counter() - t0


async def run(uri: str, clients: int, messages: int, payload: str) -> None:
    sem = asyncio.Semaphore(clients)

    async def bounded() -> tuple[int, float]:
        async with sem:
            return await one_client(uri, messages, payload)

    t0 = time.perf_counter()
    results = await asyncio.gather(*[bounded() for _ in range(clients)])
    elapsed = time.perf_counter() - t0
    total_ok = sum(r[0] for r in results)
    print(
        json.dumps(
            {
                "clients": clients,
                "messages_per_client": messages,
                "total_ok_replies": total_ok,
                "wall_seconds": round(elapsed, 3),
                "uri": uri,
            },
            indent=2,
        )
    )


def main() -> None:
    p = argparse.ArgumentParser(description="WebSocket load smoke for Ethos Kernel chat")
    p.add_argument("--url", default="ws://127.0.0.1:8765/ws/chat", help="WebSocket URL")
    p.add_argument("--clients", type=int, default=10, help="Concurrent connections")
    p.add_argument("--messages", type=int, default=3, help="Messages per connection")
    p.add_argument(
        "--text",
        default="Load test ping: hello from ws_stress.py",
        help="User text field",
    )
    args = p.parse_args()
    asyncio.run(run(args.url, args.clients, args.messages, args.text))


if __name__ == "__main__":
    main()
