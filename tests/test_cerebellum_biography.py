"""Tests for cerebellum biography matrix overlay."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.modules.cerebellum_biography import (
    CerebellumBiographyMatrix,
    somatic_biography_overlay,
)
from src.modules.narrative import NarrativeMemory


def test_cerebellum_biography_augment_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_CEREBELLUM_BIOGRAPHY", raising=False)
    mem = NarrativeMemory(db_path=":memory:")
    with tempfile.TemporaryDirectory() as td:
        p = str(Path(td) / "bio.json")
        cb = CerebellumBiographyMatrix(memory=mem, storage_path=p)
        assert cb.augment_signals({"calm": 0.5}) == {"calm": 0.5}


def test_cerebellum_biography_persistence_and_coherence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_CEREBELLUM_BIOGRAPHY", "1")
    mem = NarrativeMemory(db_path=":memory:")
    with tempfile.TemporaryDirectory() as td:
        p = str(Path(td) / "bio.json")
        cb = CerebellumBiographyMatrix(memory=mem, storage_path=p)
        out = cb.augment_signals({"calm": 0.5})
        assert "cerebellum_identity_coherence" in out
        assert "calm" in out
        cb.after_decision(expected_impact=0.1, register_episode=True)
        cb2 = CerebellumBiographyMatrix(memory=mem, storage_path=p)
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        assert "coherence_ema" in data
        assert cb2._state.last_impact_sample == pytest.approx(0.1)


def test_swarm_sync_tail_persisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_CEREBELLUM_BIOGRAPHY_PATH", raising=False)
    mem = NarrativeMemory(db_path=":memory:")
    with tempfile.TemporaryDirectory() as td:
        p = str(Path(td) / "bio.json")
        cb = CerebellumBiographyMatrix(memory=mem, storage_path=p)
        cb.append_swarm_sync("hello swarm", source="pytest")
        cb2 = CerebellumBiographyMatrix(memory=mem, storage_path=p)
        assert len(cb2._state.swarm_sync_tail) == 1
        assert cb2._state.swarm_sync_tail[0]["msg"] == "hello swarm"
        ov = cb2.somatic_state_overlay()
        assert ov["cerebellum_swarm_sync_count"] == 1
        assert ov["cerebellum_last_swarm_sync_iso"]


def test_somatic_biography_overlay_reads_default_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with tempfile.TemporaryDirectory() as td:
        p = str(Path(td) / "x.json")
        monkeypatch.setenv("KERNEL_CEREBELLUM_BIOGRAPHY_PATH", p)
        CerebellumBiographyMatrix(memory=None, storage_path=p).append_swarm_sync("x", source="t")
        monkeypatch.setenv("KERNEL_CEREBELLUM_BIOGRAPHY_PATH", p)
        ov = somatic_biography_overlay()
        assert ov["cerebellum_swarm_sync_count"] == 1
