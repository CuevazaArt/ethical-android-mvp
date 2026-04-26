"""
Ethos 2.0 — Project Status (ground truth)

Run: python -m src.core.status

Reports actual state of the project, independent of CONTEXT.md.
Any L1 in any IDE can run this to know exactly where things stand.
"""

from __future__ import annotations

import subprocess
import sys


def _check(label: str, fn) -> bool:
    try:
        result = fn()
        symbol = "✅" if result else "❌"
        print(f"  {symbol} {label}")
        return bool(result)
    except Exception as e:
        print(f"  ❌ {label} — {e}")
        return False


def _importable(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def _ollama_reachable() -> bool:
    import httpx

    try:
        r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


def _run_tests() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/core/", "-q", "--tb=no"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else "no output"
    return r.returncode == 0, last_line


def main() -> None:
    if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 50)
    print("  ETHOS 2.0 — Project Status")
    print("=" * 50)

    # Core modules
    print("\nCore modules:")
    modules = [
        "src.core.llm",
        "src.core.ethics",
        "src.core.memory",
        "src.core.chat",
        "src.core.identity",
        "src.core.vision",
        "src.core.safety",
        "src.core.perception",
        "src.core.user_model",
        "src.core.vault",
    ]
    core_ok = all(_check(m.split(".")[-1], lambda m=m: _importable(m)) for m in modules)

    # Sensory modules
    print("\nSensory modules:")
    sensory = ["src.core.stt", "src.core.tts"]
    sensory_ok = all(_check(m.split(".")[-1], lambda m=m: _importable(m)) for m in sensory)

    # Tests
    print("\nTests:")
    tests_pass, test_summary = _run_tests()
    symbol = "✅" if tests_pass else "❌"
    print(f"  {symbol} {test_summary}")

    # Ollama
    print("\nInfrastructure:")
    ollama_ok = _check("Ollama reachable", _ollama_reachable)

    # Memory state
    try:
        from src.core.identity import Identity
        from src.core.memory import Memory
        from src.core.user_model import UserModelTracker
        from src.core.vault import SecureVault

        mem = Memory()
        ident = Identity()
        user_mod = UserModelTracker()
        vault = SecureVault()

        print(f"  📝 Memory: {len(mem)} episodes stored")
        print(
            f"  🧠 Identity: {len(ident._journal)} journal entries, {len(ident._chronicle)} chronicles"
        )
        if ident._archetype:
            print(f"  👑 Archetype: {ident._archetype}")

        print(
            f"  👤 User Model: Risk [{user_mod.risk_band.value}], Bias [{user_mod.cognitive_pattern.value}], Turns [{user_mod.turns_observed}]"
        )
        print(f"  🔒 Vault: {len(vault.list_keys())} protected keys")

    except Exception:
        print("  📝 System state: partially initialized")

    # Phase assessment
    print("\nPhase assessment:")
    if not core_ok:
        print("  🔴 Core modules broken — fix before anything else")
    elif not tests_pass:
        print("  🟡 Core importable but tests failing")
    elif not ollama_ok:
        print("  🟡 Code ready — Ollama not running (start: ollama serve)")
    elif not sensory_ok:
        print("  🟡 Core complete — Sensory modules (STT/TTS) pending")
    else:
        print("  🟢 V2 Core Refinement — Recursive Identity & User Modeling active")

    print()


if __name__ == "__main__":
    main()
