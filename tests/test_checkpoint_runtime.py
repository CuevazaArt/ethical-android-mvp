"""Checkpoint env wiring and autosave (Fase 2.4)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.persistence.checkpoint import (
    autosave_interval_episodes,
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    should_load_checkpoint,
    should_save_on_disconnect,
    try_save_checkpoint,
)
from src.simulations.runner import ALL_SIMULATIONS


def test_checkpoint_env_disabled_by_default(monkeypatch):
    monkeypatch.delenv("KERNEL_CHECKPOINT_PATH", raising=False)
    assert should_load_checkpoint() is False
    assert should_save_on_disconnect() is False
    assert autosave_interval_episodes() == 0


def test_autosave_every_n_episodes(tmp_path, monkeypatch):
    monkeypatch.setenv("KERNEL_CHECKPOINT_PATH", str(tmp_path / "ckpt.json"))
    monkeypatch.setenv("KERNEL_CHECKPOINT_EVERY_N_EPISODES", "1")

    k = EthicalKernel(variability=False)
    state = init_session_checkpoint_state(k)
    maybe_autosave_episodes(k, state)
    assert not (tmp_path / "ckpt.json").is_file()

    scn = ALL_SIMULATIONS[1]()
    k.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)
    maybe_autosave_episodes(k, state)
    assert (tmp_path / "ckpt.json").is_file()


def test_try_save_explicit(tmp_path, monkeypatch):
    monkeypatch.setenv("KERNEL_CHECKPOINT_PATH", str(tmp_path / "x.json"))
    k = EthicalKernel(variability=False)
    assert try_save_checkpoint(k) is True
    assert (tmp_path / "x.json").is_file()
