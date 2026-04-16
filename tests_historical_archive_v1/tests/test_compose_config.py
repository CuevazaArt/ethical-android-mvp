"""Validate Docker Compose file merges (requires Docker CLI + Compose v2 on PATH)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _docker_on_path() -> bool:
    return shutil.which("docker") is not None


def _compose_config_quiet(files: list[str], *, profile: str | None = None) -> None:
    cmd = ["docker", "compose"]
    for f in files:
        cmd.extend(["-f", str(ROOT / f)])
    if profile:
        cmd.extend(["--profile", profile])
    cmd.extend(["config", "--quiet"])
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)


@pytest.mark.skipif(not _docker_on_path(), reason="docker not on PATH")
def test_compose_merge_base_prodish(tmp_path, monkeypatch):
    """prodish uses `env_file: .env`; use a throwaway copy so we never clobber a developer .env."""
    monkeypatch.chdir(ROOT)
    env_target = ROOT / ".env"
    env_backup = tmp_path / "env.backup"
    example = ROOT / ".env.example"
    had_user_env = env_target.exists()
    if had_user_env:
        env_backup.write_bytes(env_target.read_bytes())
    try:
        env_target.write_bytes(example.read_bytes())
        _compose_config_quiet(["docker-compose.yml", "docker-compose.prodish.yml"])
    finally:
        if had_user_env:
            env_target.write_bytes(env_backup.read_bytes())
        else:
            env_target.unlink(missing_ok=True)


@pytest.mark.skipif(not _docker_on_path(), reason="docker not on PATH")
def test_compose_merge_base_prodish_metrics(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    env_target = ROOT / ".env"
    env_backup = tmp_path / "env.backup"
    example = ROOT / ".env.example"
    had_user_env = env_target.exists()
    if had_user_env:
        env_backup.write_bytes(env_target.read_bytes())
    try:
        env_target.write_bytes(example.read_bytes())
        _compose_config_quiet(
            [
                "docker-compose.yml",
                "docker-compose.prodish.yml",
                "docker-compose.metrics.yml",
            ]
        )
    finally:
        if had_user_env:
            env_target.write_bytes(env_backup.read_bytes())
        else:
            env_target.unlink(missing_ok=True)


@pytest.mark.skipif(not _docker_on_path(), reason="docker not on PATH")
def test_compose_merge_base_metrics_only():
    _compose_config_quiet(["docker-compose.yml", "docker-compose.metrics.yml"])


@pytest.mark.skipif(not _docker_on_path(), reason="docker not on PATH")
def test_compose_prodish_with_llm_profile(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    env_target = ROOT / ".env"
    env_backup = tmp_path / "env.backup"
    example = ROOT / ".env.example"
    had_user_env = env_target.exists()
    if had_user_env:
        env_backup.write_bytes(env_target.read_bytes())
    try:
        env_target.write_bytes(example.read_bytes())
        _compose_config_quiet(
            ["docker-compose.yml", "docker-compose.prodish.yml"],
            profile="llm",
        )
    finally:
        if had_user_env:
            env_target.write_bytes(env_backup.read_bytes())
        else:
            env_target.unlink(missing_ok=True)
