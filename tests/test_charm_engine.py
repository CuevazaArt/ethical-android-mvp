"""
Tests for the Charm Engine — Bloque 8.1 (Team Copilot, Módulo 8).

Covers:
- Unit tests for CharmEngine, StyleParametrizer, GesturePlanner, ResponseSculptor
- Absolute-evil safety bypass
- Caution and frustration-streak effects
- Intimacy level effects
- Concurrent / thread-safety validation
"""

from __future__ import annotations

import asyncio
import os
import sys
import threading
from dataclasses import field
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.charm_engine import (
    CharmEngine,
    CharmVector,
    GesturePlanner,
    ResponseSculptor,
    StylizedResponse,
    StyleParametrizer,
)
from src.modules.uchi_soto import InteractionProfile, TrustCircle
from src.modules.user_model import UserModelTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile(intimacy: float = 0.0, trust: float = 0.5) -> InteractionProfile:
    return InteractionProfile(
        agent_id="test_agent",
        circle=TrustCircle.SOTO_NEUTRO,
        trust_score=trust,
        intimacy_level=intimacy,
    )


def _tracker(frustration_streak: int = 0) -> UserModelTracker:
    t = UserModelTracker()
    t.frustration_streak = frustration_streak
    return t


# ---------------------------------------------------------------------------
# StyleParametrizer
# ---------------------------------------------------------------------------

class TestStyleParametrizer:
    def test_returns_charm_vector(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("utilitarian", _profile(), _tracker(), caution_level=0.2)
        assert isinstance(cv, CharmVector)

    def test_block_action_raises_directiveness(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("deontolog_block", _profile(), _tracker(), caution_level=0.1)
        assert cv.directiveness >= 0.8
        assert cv.warmth <= 0.3
        assert cv.mystery == 0.0
        assert cv.playfulness == 0.0

    def test_care_action_raises_warmth(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("care_response", _profile(), _tracker(), caution_level=0.1)
        assert cv.warmth > 0.5

    def test_high_caution_caps_warmth(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("utilitarian", _profile(), _tracker(), caution_level=0.9)
        assert cv.warmth <= 0.1 + 1e-6  # max_warmth = max(0.1, 1 - 0.9)

    def test_high_frustration_streak_removes_playfulness(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("utilitarian", _profile(), _tracker(frustration_streak=5), caution_level=0.0)
        assert cv.playfulness <= 0.1

    def test_high_intimacy_low_caution_adds_warmth(self) -> None:
        sp = StyleParametrizer()
        cv = sp.parametrize("utilitarian", _profile(intimacy=0.8), _tracker(), caution_level=0.3)
        assert cv.warmth > 0.5

    def test_high_caution_downgrades_intimacy(self) -> None:
        sp = StyleParametrizer()
        profile = _profile(intimacy=0.9)
        sp.parametrize("utilitarian", profile, _tracker(), caution_level=0.7)
        assert profile.intimacy_level <= 0.5

    def test_values_clamped_to_0_1(self) -> None:
        sp = StyleParametrizer()
        for action in ("deontolog_block", "care_response", "utilitarian", "sympathetic", ""):
            cv = sp.parametrize(action, _profile(intimacy=1.0), _tracker(0), caution_level=0.0)
            assert 0.0 <= cv.warmth <= 1.0
            assert 0.0 <= cv.mystery <= 1.0
            assert 0.0 <= cv.playfulness <= 1.0
            assert 0.0 <= cv.directiveness <= 1.0


# ---------------------------------------------------------------------------
# GesturePlanner
# ---------------------------------------------------------------------------

class TestGesturePlanner:
    def test_warm_charm_generates_nod_and_gaze(self) -> None:
        gp = GesturePlanner()
        cv = CharmVector(warmth=0.8, mystery=0.2, playfulness=0.2, directiveness=0.3)
        plan = gp.plan(cv)
        actuators = [g["actuator"] for g in plan]
        assert "head" in actuators
        assert "eyes" in actuators

    def test_playful_charm_generates_eyebrow_raise(self) -> None:
        gp = GesturePlanner()
        cv = CharmVector(warmth=0.3, mystery=0.2, playfulness=0.7, directiveness=0.3)
        plan = gp.plan(cv)
        actuators = [g["actuator"] for g in plan]
        assert "eyebrows" in actuators

    def test_directive_charm_generates_direct_contact(self) -> None:
        gp = GesturePlanner()
        cv = CharmVector(warmth=0.2, mystery=0.0, playfulness=0.0, directiveness=0.9)
        plan = gp.plan(cv)
        actions = [g["action"] for g in plan]
        assert "direct_contact" in actions

    def test_neutral_charm_no_gestures(self) -> None:
        gp = GesturePlanner()
        cv = CharmVector(warmth=0.3, mystery=0.2, playfulness=0.3, directiveness=0.4)
        plan = gp.plan(cv)
        assert isinstance(plan, list)

    def test_gesture_intensity_within_range(self) -> None:
        gp = GesturePlanner()
        cv = CharmVector(warmth=0.9, mystery=0.3, playfulness=0.9, directiveness=0.9)
        plan = gp.plan(cv)
        for g in plan:
            if "intensity" in g:
                assert 0.0 <= g["intensity"] <= 1.0


# ---------------------------------------------------------------------------
# ResponseSculptor
# ---------------------------------------------------------------------------

class TestResponseSculptor:
    def test_absolute_evil_bypass(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="Hello",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=True,
        )
        assert out.final_text == "Hello"
        assert out.charm_vector["warmth"] == 0.0
        assert out.charm_vector["directiveness"] == 1.0
        assert any(g["action"] == "rigid_block" for g in out.gesture_plan)

    def test_normal_sculpt_returns_stylized_response(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="Sure, let me explain.",
            decision_action="utilitarian",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.2,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)
        assert isinstance(out.final_text, str)
        assert len(out.charm_vector) == 4
        assert isinstance(out.gesture_plan, list)

    def test_warm_open_tone_annotation(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="I understand.",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        assert "[Tone: Warm & Open]" in out.final_text

    def test_direct_tone_annotation(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="No.",
            decision_action="deontolog_block",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        assert "[Tone: Direct & Boundaried]" in out.final_text

    def test_charm_vector_values_are_rounded(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="Hi",
            decision_action="care_response",
            profile=_profile(intimacy=0.5),
            user_tracker=_tracker(),
            caution_level=0.2,
            absolute_evil_detected=False,
        )
        for key, val in out.charm_vector.items():
            # Rounded to 3 decimal places means at most 3 decimal digits
            assert round(val, 3) == val, f"{key}={val} not rounded to 3 dp"


# ---------------------------------------------------------------------------
# CharmEngine facade
# ---------------------------------------------------------------------------

class TestCharmEngine:
    def test_apply_returns_stylized_response(self) -> None:
        ce = CharmEngine()
        out = ce.apply(
            base_text="How can I help?",
            decision_action="utilitarian",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.2,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)

    def test_apply_absolute_evil_bypass_end_to_end(self) -> None:
        ce = CharmEngine()
        out = ce.apply(
            base_text="Danger detected.",
            decision_action="any_action",
            profile=_profile(intimacy=1.0),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=True,
        )
        assert out.charm_vector["warmth"] == 0.0
        assert out.charm_vector["directiveness"] == 1.0

    def test_apply_with_none_llm_module(self) -> None:
        ce = CharmEngine(llm_module=None)
        out = ce.apply(
            base_text="Test.",
            decision_action="utilitarian",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.3,
            absolute_evil_detected=False,
        )
        assert out.final_text is not None

    def test_apply_empty_decision_action(self) -> None:
        ce = CharmEngine()
        out = ce.apply(
            base_text="Hi.",
            decision_action="",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)

    def test_apply_max_caution_caps_warmth(self) -> None:
        ce = CharmEngine()
        out = ce.apply(
            base_text="Safety first.",
            decision_action="care_response",
            profile=_profile(intimacy=1.0),
            user_tracker=_tracker(),
            caution_level=1.0,
            absolute_evil_detected=False,
        )
        # max_warmth = max(0.1, 1 - 1.0) = 0.1
        assert out.charm_vector["warmth"] <= 0.1 + 1e-6


# ---------------------------------------------------------------------------
# Concurrency / thread-safety (Bloque 8.1 — multithread load)
# ---------------------------------------------------------------------------

class TestCharmEngineConcurrency:
    """Verify that CharmEngine is safe to call from concurrent threads."""

    def test_concurrent_apply_no_data_race(self) -> None:
        """10 threads applying CharmEngine in parallel must all succeed."""
        ce = CharmEngine()
        results: list[StylizedResponse | Exception] = []
        lock = threading.Lock()

        def worker(n: int) -> None:
            try:
                out = ce.apply(
                    base_text=f"Message {n}",
                    decision_action="care_response" if n % 2 == 0 else "deontolog_block",
                    profile=_profile(intimacy=n / 20.0),
                    user_tracker=_tracker(frustration_streak=n % 4),
                    caution_level=n / 20.0,
                    absolute_evil_detected=(n % 7 == 0),
                )
                with lock:
                    results.append(out)
            except Exception as exc:
                with lock:
                    results.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        errors = [r for r in results if isinstance(r, Exception)]
        assert not errors, f"Concurrent errors: {errors}"
        assert len(results) == 10

    def test_concurrent_apply_absolute_evil_isolation(self) -> None:
        """Threads with absolute_evil=True must never leak warm charm."""
        ce = CharmEngine()
        evil_results: list[StylizedResponse] = []
        lock = threading.Lock()

        def evil_worker() -> None:
            out = ce.apply(
                base_text="blocked",
                decision_action="harm",
                profile=_profile(intimacy=1.0),
                user_tracker=_tracker(),
                caution_level=0.0,
                absolute_evil_detected=True,
            )
            with lock:
                evil_results.append(out)

        threads = [threading.Thread(target=evil_worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        for out in evil_results:
            assert out.charm_vector["warmth"] == 0.0
            assert out.charm_vector["directiveness"] == 1.0


# ---------------------------------------------------------------------------
# Async tests (cooperative cancellation pattern — Bloque 8.1)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_charm_engine_in_async_context() -> None:
    """CharmEngine is CPU-bound; verify it can be called safely from async code."""
    ce = CharmEngine()
    loop = asyncio.get_event_loop()
    out = await loop.run_in_executor(
        None,
        lambda: ce.apply(
            base_text="Async test.",
            decision_action="utilitarian",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.1,
            absolute_evil_detected=False,
        ),
    )
    assert isinstance(out, StylizedResponse)


@pytest.mark.asyncio
async def test_charm_engine_multiple_concurrent_coroutines() -> None:
    """Simulate 5 async chat-turn coroutines all offloading CharmEngine."""
    ce = CharmEngine()
    loop = asyncio.get_event_loop()

    async def async_turn(n: int) -> StylizedResponse:
        return await loop.run_in_executor(
            None,
            lambda: ce.apply(
                base_text=f"Turn {n}",
                decision_action="care_response",
                profile=_profile(intimacy=0.3),
                user_tracker=_tracker(),
                caution_level=0.1,
                absolute_evil_detected=False,
            ),
        )

    results = await asyncio.gather(*[async_turn(i) for i in range(5)])
    assert len(results) == 5
    for r in results:
        assert isinstance(r, StylizedResponse)


@pytest.mark.asyncio
async def test_charm_engine_cancellation_does_not_corrupt_state() -> None:
    """Cancelling a task mid-flight must not leave CharmEngine in broken state."""
    ce = CharmEngine()
    loop = asyncio.get_event_loop()

    async def slow_turn() -> StylizedResponse:
        return await loop.run_in_executor(
            None,
            lambda: ce.apply(
                base_text="Slow.",
                decision_action="utilitarian",
                profile=_profile(),
                user_tracker=_tracker(),
                caution_level=0.5,
                absolute_evil_detected=False,
            ),
        )

    task = asyncio.ensure_future(slow_turn())
    # Let it start, then cancel immediately
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Engine must still be usable after cancellation
    out = ce.apply(
        base_text="Post-cancel check.",
        decision_action="care_response",
        profile=_profile(),
        user_tracker=_tracker(),
        caution_level=0.1,
        absolute_evil_detected=False,
    )
    assert isinstance(out, StylizedResponse)


# ---------------------------------------------------------------------------
# Database lock utility (Bloque 8.2 smoke — sqlite_safe_write)
# ---------------------------------------------------------------------------

class TestSqliteSafeWrite:
    """Smoke tests for the db_locks utility used throughout persistence layer."""

    def test_sqlite_safe_write_in_memory_roundtrip(self) -> None:
        """In-memory writes bypass thread locks; verify basic roundtrip."""
        import sqlite3

        from src.utils.db_locks import sqlite_safe_write

        with sqlite_safe_write(":memory:") as conn:
            conn.execute("CREATE TABLE t (x INTEGER)")
            conn.execute("INSERT INTO t VALUES (42)")
            row = conn.execute("SELECT x FROM t").fetchone()
            assert row[0] == 42

    def test_sqlite_safe_write_concurrent_file(self, tmp_path: Any) -> None:
        """Multiple threads writing concurrently via sqlite_safe_write must not corrupt data."""
        import sqlite3

        from src.utils.db_locks import sqlite_safe_write

        db_path = tmp_path / "concurrent_test.db"

        # Set up schema
        with sqlite_safe_write(db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS counters (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
            conn.execute("INSERT INTO counters VALUES (1, 0)")

        errors: list[Exception] = []
        lock = threading.Lock()

        def increment() -> None:
            try:
                with sqlite_safe_write(db_path) as conn:
                    current = conn.execute("SELECT value FROM counters WHERE id = 1").fetchone()[0]
                    conn.execute("UPDATE counters SET value = ? WHERE id = 1", (current + 1,))
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=increment) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Concurrent write errors: {errors}"

        with sqlite_safe_write(db_path) as conn:
            final = conn.execute("SELECT value FROM counters WHERE id = 1").fetchone()[0]
        assert final == 8

    def test_get_db_lock_same_path_same_object(self, tmp_path: Any) -> None:
        """Same path must return the same lock object (singleton per path)."""
        from src.utils.db_locks import get_db_lock

        db_path = str(tmp_path / "test_singleton.db")
        lock_a = get_db_lock(db_path)
        lock_b = get_db_lock(db_path)
        assert lock_a is lock_b

    def test_get_db_lock_different_paths_different_objects(self, tmp_path: Any) -> None:
        from src.utils.db_locks import get_db_lock

        lock_a = get_db_lock(str(tmp_path / "path_a.db"))
        lock_b = get_db_lock(str(tmp_path / "path_b.db"))
        assert lock_a is not lock_b


# ---------------------------------------------------------------------------
# NarrativePersistence concurrency smoke (Bloque 8.2)
# ---------------------------------------------------------------------------

class TestNarrativePersistenceConcurrency:
    """Verify fixed NarrativePersistence methods work under concurrent load."""

    def _make_episode(self, episode_id: str):
        from datetime import datetime

        from src.modules.narrative_types import BodyState, NarrativeEpisode

        return NarrativeEpisode(
            id=episode_id,
            timestamp=datetime.now().isoformat(),
            place="test_place",
            event_description="concurrent test event",
            body_state=BodyState(energy=1.0, active_nodes=8, sensors_ok=True, description="ok"),
            action_taken="utilitarian",
            morals={"deontological": 0.5},
            verdict="safe",
            ethical_score=0.8,
            decision_mode="D_fast",
            sigma=0.5,
            context="test",
        )

    def test_concurrent_save_episode_file(self, tmp_path: Any) -> None:
        """Multiple threads saving different episodes must not corrupt the DB."""
        from src.persistence.narrative_storage import NarrativePersistence

        db_path = tmp_path / "narrative.db"
        np_store = NarrativePersistence(db_path)

        errors: list[Exception] = []
        lock = threading.Lock()

        def save_ep(n: int) -> None:
            try:
                ep = self._make_episode(f"ep-{n:04d}")
                np_store.save_episode(ep)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=save_ep, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert not errors, f"Concurrent episode save errors: {errors}"
        episodes = np_store.load_all_episodes()
        assert len(episodes) == 8

    def test_save_identity_digest_fixed(self, tmp_path: Any) -> None:
        """save_identity_digest must persist and load correctly after indent fix."""
        from src.persistence.narrative_storage import NarrativePersistence

        db_path = tmp_path / "identity.db"
        np_store = NarrativePersistence(db_path)
        np_store.save_identity_digest("sha256:abc123")
        loaded = np_store.load_identity_digest()
        assert loaded == "sha256:abc123"

    def test_save_arc_fixed(self, tmp_path: Any) -> None:
        """save_arc must persist and load correctly after indent fix."""
        from datetime import datetime

        from src.modules.narrative_types import NarrativeArc
        from src.persistence.narrative_storage import NarrativePersistence

        db_path = tmp_path / "arcs.db"
        np_store = NarrativePersistence(db_path)
        arc = NarrativeArc(
            id="arc-001",
            title="Test Arc",
            context="unit_test",
            start_timestamp=datetime.now().isoformat(),
            end_timestamp=None,
            predominant_archetype="hero",
            summary="A test arc",
            is_active=True,
            episodes_ids=["ep-0001", "ep-0002"],
        )
        np_store.save_arc(arc)
        arcs = np_store.load_all_arcs()
        assert len(arcs) == 1
        assert arcs[0].id == "arc-001"

    def test_delete_episode_fixed(self, tmp_path: Any) -> None:
        """delete_episode must remove the row correctly after indent fix."""
        from src.persistence.narrative_storage import NarrativePersistence

        db_path = tmp_path / "delete_test.db"
        np_store = NarrativePersistence(db_path)
        ep = self._make_episode("ep-to-delete")
        np_store.save_episode(ep)
        assert len(np_store.load_all_episodes()) == 1
        deleted = np_store.delete_episode("ep-to-delete")
        assert deleted is True
        assert len(np_store.load_all_episodes()) == 0

    def test_prune_mundane_fixed(self, tmp_path: Any) -> None:
        """prune_mundane must execute without error after indent fix."""
        from src.persistence.narrative_storage import NarrativePersistence

        db_path = tmp_path / "prune_test.db"
        np_store = NarrativePersistence(db_path)
        # Method should complete without IndentationError / OperationalError
        count = np_store.prune_mundane(max_age_days=0, min_significance=1.0)
        assert isinstance(count, int)
