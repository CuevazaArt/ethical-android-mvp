# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Kernel — Entry point V2.

Starts the interactive REPL (ChatEngine + Ollama).

Usage:
    python -m src.main
"""

import asyncio
import sys
from pathlib import Path

# Fix PYTHONPATH for direct execution (python src/main.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.core.chat import ChatEngine


async def _main() -> None:
    print("""
+----------------------------------------------------------+
|  ETHOS KERNEL V2 — Core Minimal                          |
|  Chat interactivo con conciencia ética                   |
|  2026 · MoSex Macchina Lab · Ex Machina Foundation       |
+----------------------------------------------------------+
""")
    engine = ChatEngine()
    ok = await engine.start()
    if not ok:
        print("WARN: Ollama no está disponible. Las respuestas usarán fallbacks.")
    try:
        await engine.repl()
    finally:
        await engine.close()


def main() -> None:
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\nApagando...")


if __name__ == "__main__":
    main()
