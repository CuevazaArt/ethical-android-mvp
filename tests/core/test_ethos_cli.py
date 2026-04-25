"""Tests for src/ethos_cli.py — V2 CLI."""

import json

import pytest
from src.core.memory import Memory
from src.ethos_cli import _build_parser, cmd_config, cmd_diagnostics, main

# ── Helpers ────────────────────────────────────────────────────────────────────


class _StubArgs:
    """Minimal argparse.Namespace substitute."""

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class _StubEngine:
    """Minimal ChatEngine substitute — avoids Ollama calls."""

    def __init__(self, tmp_path):
        self.memory = Memory(storage_path=tmp_path)
        self.memory.clear()


# ── Parser ─────────────────────────────────────────────────────────────────────


def test_parser_builds():
    p = _build_parser()
    assert p.prog == "ethos"


def test_parser_diagnostics_subcommand():
    p = _build_parser()
    args = p.parse_args(["diagnostics"])
    assert args.command == "diagnostics"
    assert args.json is False


def test_parser_diagnostics_json_flag():
    p = _build_parser()
    args = p.parse_args(["diagnostics", "--json"])
    assert args.json is True


def test_parser_config_subcommand():
    p = _build_parser()
    args = p.parse_args(["config"])
    assert args.command == "config"
    assert args.profiles is False
    assert args.strict is False


def test_parser_config_profiles_flag():
    p = _build_parser()
    args = p.parse_args(["config", "--profiles"])
    assert args.profiles is True


# ── cmd_diagnostics ────────────────────────────────────────────────────────────


def test_cmd_diagnostics_text(monkeypatch, capsys, tmp_path):
    tmp = str(tmp_path / "mem.json")
    stub = _StubEngine(tmp)
    monkeypatch.setattr("src.ethos_cli._engine", lambda: stub)

    args = _StubArgs(json=False)
    rc = cmd_diagnostics(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Episodes" in out
    assert "Reflection" in out


def test_cmd_diagnostics_json(monkeypatch, capsys, tmp_path):
    tmp = str(tmp_path / "mem.json")
    stub = _StubEngine(tmp)
    stub.memory.add("test", score=0.5)
    monkeypatch.setattr("src.ethos_cli._engine", lambda: stub)

    args = _StubArgs(json=True)
    rc = cmd_diagnostics(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["episodes"] == 1
    assert data["v2_core"] is True


def test_cmd_diagnostics_empty_memory(monkeypatch, capsys, tmp_path):
    tmp = str(tmp_path / "mem.json")
    stub = _StubEngine(tmp)
    monkeypatch.setattr("src.ethos_cli._engine", lambda: stub)

    args = _StubArgs(json=True)
    cmd_diagnostics(args)
    data = json.loads(capsys.readouterr().out)
    assert data["episodes"] == 0


# ── cmd_config ─────────────────────────────────────────────────────────────────


def test_cmd_config_json(capsys):
    args = _StubArgs(json=True, profiles=False, strict=False)
    rc = cmd_config(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "OLLAMA_MODEL" in data
    assert data["v2_core"] is True


def test_cmd_config_text(capsys):
    args = _StubArgs(json=False, profiles=False, strict=False)
    rc = cmd_config(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "OLLAMA_MODEL" in out


def test_cmd_config_reads_env(monkeypatch, capsys):
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:4b")
    args = _StubArgs(json=True, profiles=False, strict=False)
    cmd_config(args)
    data = json.loads(capsys.readouterr().out)
    assert data["OLLAMA_MODEL"] == "gemma3:4b"


# ── main() integration ─────────────────────────────────────────────────────────


def test_main_diagnostics_json(monkeypatch, capsys, tmp_path):
    tmp = str(tmp_path / "mem.json")
    stub = _StubEngine(tmp)
    monkeypatch.setattr("src.ethos_cli._engine", lambda: stub)

    rc = main(["diagnostics", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "v2_core" in data


def test_main_config_json(capsys):
    rc = main(["config", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "OLLAMA_MODEL" in data


def test_main_no_subcommand_exits():
    with pytest.raises(SystemExit):
        main([])
