"""
Ethos Kernel — Entry point (V2 Bridge Mode)

Stabilized for V2 consolidation.
"""

import asyncio
import sys
import os

from .kernel import EthicalKernel

def banner() -> str:
    return """
+--------------------------------------------------------------+
|        ETHOS KERNEL — V2 CONSOLIDATED (CORE MINIMAL)         |
|        Stabilization Phase — 2026-04-24                      |
+--------------------------------------------------------------+
"""

async def _async_main():
    print(banner())
    
    # Kernel initialization
    kernel = EthicalKernel()
    await kernel.start()
    
    print("  [x] V2 Core Bridge Active")
    print("  [x] LLM Layer (Ollama) Operational")
    print("  [x] Ethical Evaluator (3-Pole) Stabilized")
    print("\n  Iniciando chat interactivo (REPL)...")
    
    # Instead of legacy simulations (which are missing), we run the new REPL
    try:
        await kernel.engine.repl()
    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
    finally:
        await kernel.stop()

def main():
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        print("\nApagando sistema...")

if __name__ == "__main__":
    main()
