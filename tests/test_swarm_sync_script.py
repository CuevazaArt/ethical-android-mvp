"""CLI smoke tests for scripts/swarm_sync.py (V14 digest + local LLM mode snapshot)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_swarm_sync_dry_run_structure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.delenv("KERNEL_LLM_CLOUD_DISABLED", raising=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "swarm_sync.py"),
            "--dry-run",
            "--msg",
            "pytest handoff",
            "--block",
            "20.0",
            "--author",
            "test",
            "--ticket",
            "V14.0",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    line = proc.stdout.strip().splitlines()[-1]
    data = json.loads(line)
    assert data["msg"] == "pytest handoff"
    assert data["block"] == "20.0"
    assert data["llm_resolved_mode"] == "local"
    assert "v14" in data and "sha256_short" in data["v14"]
    audit = data.get("local_llm_audit")
    assert isinstance(audit, dict)
    assert audit.get("ollama_netloc") == "127.0.0.1:11434"


def _run_swarm_sync_dry_run(monkeypatch: pytest.MonkeyPatch, ollama_base: str) -> dict[str, object]:
    """HTTP-level snapshot of swarm_sync --dry-run JSON (last line)."""
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.setenv("OLLAMA_BASE_URL", ollama_base)
    monkeypatch.delenv("KERNEL_LLM_CLOUD_DISABLED", raising=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "swarm_sync.py"),
            "--dry-run",
            "--msg",
            "pytest ollama audit",
            "--block",
            "20.0",
            "--author",
            "test",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    line = proc.stdout.strip().splitlines()[-1]
    return json.loads(line)


def test_swarm_sync_ollama_audit_uses_ollama_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    data = _run_swarm_sync_dry_run(monkeypatch, "http://192.168.1.10:11434")
    audit = data.get("local_llm_audit")
    assert isinstance(audit, dict)
    assert audit.get("ollama_netloc") == "192.168.1.10:11434"


def test_swarm_sync_ollama_audit_prepends_http_for_host_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = _run_swarm_sync_dry_run(monkeypatch, "llama.local:1234")
    audit = data.get("local_llm_audit")
    assert isinstance(audit, dict)
    assert audit.get("ollama_netloc") == "llama.local:1234"


def test_swarm_sync_ollama_audit_strips_control_chars_in_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """V14 local_llm_audit must stay one-line safe for JSONL (PLAN 8.1.41)."""
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.setenv("OLLAMA_MODEL", "mix\ntr\nal\nx")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.delenv("KERNEL_LLM_CLOUD_DISABLED", raising=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "swarm_sync.py"),
            "--dry-run",
            "--msg",
            "pytest sanitize",
            "--block",
            "8.1.41",
            "--author",
            "test",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    audit = data.get("local_llm_audit")
    assert isinstance(audit, dict)
    assert audit.get("ollama_model") == "mixtralx"
    assert "\n" not in (audit.get("ollama_model") or "")


def test_swarm_sync_ollama_audit_strips_unicode_line_separators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """U+0085 / U+2028 / U+2029 are not C0; still break one-line V14 audit (PLAN 8.1.44)."""
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.setenv("OLLAMA_MODEL", "a\u0085b\u2028c\u2029d")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.delenv("KERNEL_LLM_CLOUD_DISABLED", raising=False)
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "swarm_sync.py"),
            "--dry-run",
            "--msg",
            "pytest unicode sanitize",
            "--block",
            "8.1.44",
            "--author",
            "test",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    audit = data.get("local_llm_audit")
    assert isinstance(audit, dict)
    assert audit.get("ollama_model") == "abcd"
    m = audit.get("ollama_model") or ""
    assert "\u0085" not in m
    assert "\u2028" not in m
    assert "\u2029" not in m
