"""
Tests for the identity-restore gap closure and Phase 7 vertical additions.

Covers:
  - ImmortalityProtocol._apply_snapshot restores full NarrativeIdentityState
    (leans + core beliefs) — gap closed April 2026
  - ImmortalityProtocol version bumped to 3.2 after identity_state_json added
  - identity_state_json is included in the integrity hash (tamper detection)
  - IdentityReflector.get_subjective_tone blends historical arcs (not just active)
  - IdentityReflector.threshold_context exposes signed lean deltas
  - NarrativeMemory.get_theater_math_context merges tone + deltas (Phase 7 bridge)
  - NarrativeIdentityState.core_beliefs uses field(default_factory=list) — no mutation
"""

import json
import types
import pytest

from src.modules.narrative_identity import NarrativeIdentityState, NarrativeIdentityTracker
from src.modules.narrative_types import NarrativeArc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_memory(tmp_path):
    """Build a NarrativeMemory backed by a temp SQLite db."""
    from src.modules.narrative import NarrativeMemory
    return NarrativeMemory(db_path=tmp_path / "test.db")


def _make_kernel_stub(memory):
    """
    Minimal kernel stub carrying only the attributes ImmortalityProtocol touches.
    Avoids importing the full EthicalKernel and its heavy dependencies.
    """
    import numpy as np

    class _Bayesian:
        pruning_threshold = 0.3
        hypothesis_weights = np.array([0.33, 0.33, 0.34])

    class _Locus:
        alpha = 0.6
        beta = 0.4

    class _Poles:
        base_weights = {"utilitarian": 0.5, "deontological": 0.3, "virtue": 0.2}

    kernel = types.SimpleNamespace(
        memory=memory,
        bayesian=_Bayesian(),
        locus=_Locus(),
        poles=_Poles(),
    )
    return kernel


# ---------------------------------------------------------------------------
# 1. NarrativeIdentityState — mutable default fix
# ---------------------------------------------------------------------------

class TestNarrativeIdentityStateMutableDefault:
    def test_two_instances_have_independent_belief_lists(self):
        """field(default_factory=list) prevents shared mutable state."""
        s1 = NarrativeIdentityState()
        s2 = NarrativeIdentityState()
        s1.core_beliefs.append({"id": "X", "text": "test", "significance": 0.9})
        assert s2.core_beliefs == [], "s2 must not share s1's list"

    def test_none_value_normalised_in_post_init(self):
        """Passing core_beliefs=None explicitly is handled gracefully."""
        s = NarrativeIdentityState(core_beliefs=None)
        assert s.core_beliefs == []


# ---------------------------------------------------------------------------
# 2. ImmortalityProtocol — identity_state_json in Snapshot
# ---------------------------------------------------------------------------

class TestImmortalitySnapshotVersion:
    def test_backup_version_is_3_2(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        kernel = _make_kernel_stub(mem)

        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        assert snap.version == "3.2", "Version must be 3.2 after identity_state_json addition"

    def test_backup_includes_identity_state_json(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        # Seed some leans via an episode
        mem.register("lab", "test event", "helped", {"care": "always help"},
                     "Good", 0.8, "D_fast", 0.7, "everyday")

        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        payload = json.loads(snap.identity_state_json)
        assert "civic_lean" in payload
        assert "care_lean" in payload
        assert "core_beliefs" in payload
        assert isinstance(payload["core_beliefs"], list)

    def test_identity_state_json_in_integrity_hash_input(self, tmp_path):
        """
        Changing identity_state_json must produce a different hash,
        proving it is part of the signed payload.
        """
        from src.modules.immortality import ImmortalityProtocol, Snapshot

        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))

        # Build two identical snapshots differing only in identity_state_json
        base_kwargs = dict(
            id="SNAP-0001", timestamp="2026-04-14T00:00:00", version="3.2",
            episodes_count=5, last_episode_id="EP-0005",
            experience_digest="digest", active_arc_id="ARC-001",
            pruning_threshold=0.3, hypothesis_weights=[0.33, 0.33, 0.34],
            alpha_locus=0.6, beta_locus=0.4, negative_load=0.0,
            forgiven_memories=0, weakness_type="indecisive",
            weakness_intensity=0.25, emotional_load=0.0,
            pole_weights={"utilitarian": 0.5},
        )
        snap_a = Snapshot(**base_kwargs, identity_state_json="{}")
        snap_b = Snapshot(**base_kwargs, identity_state_json='{"civic_lean": 0.9}')

        hash_a = protocol._calculate_hash(snap_a)
        hash_b = protocol._calculate_hash(snap_b)
        assert hash_a != hash_b, "Different identity states must yield different hashes"


# ---------------------------------------------------------------------------
# 3. ImmortalityProtocol — full identity restore
# ---------------------------------------------------------------------------

class TestImmortalityIdentityRestore:
    def test_restore_preserves_civic_lean(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        # Register civic episodes to push lean above default 0.5
        for _ in range(6):
            mem.register("city", "helped citizen", "assisted", {"civic": "duty"},
                         "Good", 0.85, "D_fast", 0.6, "everyday")

        original_lean = mem.identity.state.civic_lean
        assert original_lean > 0.5, "Pre-condition: civic lean should have risen"

        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        # Reset identity tracker to default
        mem.identity.import_state(NarrativeIdentityState())
        assert mem.identity.state.civic_lean == 0.5, "Pre-condition: tracker reset"

        # Restore
        protocol._apply_snapshot(kernel, snap)

        restored = mem.identity.state.civic_lean
        assert abs(restored - original_lean) < 0.001, (
            f"Civic lean not restored: expected {original_lean}, got {restored}"
        )

    def test_restore_preserves_care_lean(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        for _ in range(5):
            mem.register("hospital", "emergency", "assisted",
                         {"care": "compassion"}, "Good", 0.9, "D_fast", 0.8, "emergency")

        original_care = mem.identity.state.care_lean
        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        mem.identity.import_state(NarrativeIdentityState())
        protocol._apply_snapshot(kernel, snap)

        assert abs(mem.identity.state.care_lean - original_care) < 0.001

    def test_restore_preserves_episode_count(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        for i in range(4):
            mem.register(f"loc{i}", f"event{i}", f"action{i}", {}, "Good",
                         0.5, "D_fast", 0.5, "everyday")

        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        mem.identity.import_state(NarrativeIdentityState())
        protocol._apply_snapshot(kernel, snap)

        assert mem.identity.state.episode_count == 4

    def test_restore_preserves_core_beliefs(self, tmp_path):
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        # Inject a high-significance episode with morals (Phase 6 Core Beliefs)
        ep = mem.register("crisis", "bomb threat", "evacuated",
                          {"duty": "protect civilians"}, "Good",
                          0.95, "D_delib", 0.95, "emergency")
        # Force significance high enough to crystallize belief
        ep.significance = 0.9
        mem.identity.update_from_episode(ep)

        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        snap = protocol.backup(kernel)

        # Wipe beliefs
        mem.identity.import_state(NarrativeIdentityState())

        protocol._apply_snapshot(kernel, snap)

        payload = json.loads(snap.identity_state_json)
        restored_beliefs = mem.identity.state.core_beliefs
        assert len(restored_beliefs) == len(payload["core_beliefs"]), (
            "Core beliefs count mismatch after restore"
        )

    def test_restore_graceful_on_empty_identity_json(self, tmp_path):
        """_restore_identity_state with '{}' must not crash or corrupt state."""
        from src.modules.immortality import ImmortalityProtocol

        mem = _make_memory(tmp_path)
        kernel = _make_kernel_stub(mem)
        protocol = ImmortalityProtocol(str(tmp_path / "immortality.json"))
        # Should not raise
        protocol._restore_identity_state(kernel, "{}")
        protocol._restore_identity_state(kernel, "")


# ---------------------------------------------------------------------------
# 4. IdentityReflector — historical arc tone blend
# ---------------------------------------------------------------------------

class TestSubjectiveToneHistoricalBlend:
    def _build_memory_with_arcs(self, tmp_path):
        """Build a NarrativeMemory with a closed 'hero' arc and an active 'care' arc."""
        mem = _make_memory(tmp_path)
        # Closed arc with archetype "hero"
        closed = NarrativeArc(
            id="ARC-001", title="The Heroic Period", context="emergency",
            episodes_ids=["EP-0001"],
            start_timestamp="2026-04-01T00:00:00",
            end_timestamp="2026-04-05T00:00:00",
            predominant_archetype="hero",
            is_active=False,
        )
        # Active arc with archetype "care"
        active = NarrativeArc(
            id="ARC-002", title="The Care Period", context="everyday",
            episodes_ids=["EP-0002"],
            start_timestamp="2026-04-10T00:00:00",
            predominant_archetype="care",
            is_active=True,
        )
        mem.arcs = [closed, active]
        mem.active_arc = active
        return mem

    def test_tone_contains_active_arc_archetype(self, tmp_path):
        mem = self._build_memory_with_arcs(tmp_path)
        tone = mem.get_subjective_tone()
        # 'care' maps to 'caring' via _ARCHETYPE_TO_TONE
        assert "caring" in tone, "Active arc 'care' must appear as 'caring' in tone"

    def test_tone_contains_closed_arc_archetype(self, tmp_path):
        mem = self._build_memory_with_arcs(tmp_path)
        tone = mem.get_subjective_tone()
        # 'hero' maps to 'heroic' via _ARCHETYPE_TO_TONE
        assert "heroic" in tone, "Closed arc 'hero' must be translated to 'heroic' in tone"

    def test_tone_sums_to_one(self, tmp_path):
        mem = self._build_memory_with_arcs(tmp_path)
        tone = mem.get_subjective_tone()
        assert abs(sum(tone.values()) - 1.0) < 0.01, "Tone weights must sum to 1.0"

    def test_active_arc_dominates_over_history(self, tmp_path):
        mem = self._build_memory_with_arcs(tmp_path)
        tone = mem.get_subjective_tone()
        # Active arc 'care'→'caring' weight=1.0; closed 'hero'→'heroic' weight=0.5
        assert tone.get("caring", 0) > tone.get("heroic", 0), (
            "Active arc must have higher weight than closed arc"
        )

    def test_tone_neutral_when_no_arcs(self, tmp_path):
        mem = _make_memory(tmp_path)
        tone = mem.get_subjective_tone()
        assert tone == {"neutral": 1.0}

    def test_tone_with_three_closed_arcs(self, tmp_path):
        """Decay chain: weights 0.5 -> 0.25 -> 0.125 for three closed arcs."""
        mem = _make_memory(tmp_path)
        archetypes = ["warrior", "sage", "trickster"]
        for i, arch in enumerate(archetypes):
            mem.arcs.append(NarrativeArc(
                id=f"ARC-{i:03d}", title=arch, context="context",
                episodes_ids=[],
                start_timestamp=f"2026-04-0{i+1}T00:00:00",
                end_timestamp=f"2026-04-0{i+2}T00:00:00",
                predominant_archetype=arch,
                is_active=False,
            ))
        # No active arc
        mem.active_arc = None

        tone = mem.get_subjective_tone()
        # 'trickster' maps to 'playful' via _ARCHETYPE_TO_TONE
        assert "playful" in tone
        assert tone["playful"] > tone.get("contemplative", 0)  # trickster > sage
        assert abs(sum(tone.values()) - 1.0) < 0.01


# ---------------------------------------------------------------------------
# 5. Theater→Math bridge: threshold_context + get_theater_math_context
# ---------------------------------------------------------------------------

class TestTheaterMathBridge:
    def test_threshold_context_returns_four_deltas(self, tmp_path):
        from src.modules.identity_reflection import IdentityReflector
        mem = _make_memory(tmp_path)
        reflector = IdentityReflector(mem)
        ctx = reflector.threshold_context()
        assert set(ctx.keys()) == {"civic_delta", "care_delta",
                                   "deliberation_delta", "careful_delta"}

    def test_threshold_context_neutral_at_start(self, tmp_path):
        from src.modules.identity_reflection import IdentityReflector
        mem = _make_memory(tmp_path)
        reflector = IdentityReflector(mem)
        ctx = reflector.threshold_context()
        # All leans start at 0.5 → all deltas should be ~0
        for key, val in ctx.items():
            assert abs(val) < 0.01, f"{key} should be ~0 at init, got {val}"

    def test_threshold_context_rises_after_civic_episodes(self, tmp_path):
        mem = _make_memory(tmp_path)
        for _ in range(10):
            mem.register("city", "helped", "assisted", {"civic": "duty"},
                         "Good", 0.9, "D_fast", 0.6, "everyday")
        ctx = mem.get_theater_math_context()
        assert ctx["civic_delta"] > 0, "Civic delta must be positive after civic episodes"

    def test_theater_math_context_contains_tone_keys(self, tmp_path):
        mem = _make_memory(tmp_path)
        # Register one episode to create an arc
        mem.register("park", "walk", "observed", {}, "Good", 0.5, "D_fast", 0.5, "everyday")
        ctx = mem.get_theater_math_context()
        # Must have at least one tone_ key
        tone_keys = [k for k in ctx if k.startswith("tone_")]
        assert len(tone_keys) >= 1

    def test_theater_math_context_all_values_finite(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.register("lab", "run tests", "reported", {}, "Good", 0.3, "D_fast", 0.4, "everyday")
        ctx = mem.get_theater_math_context()
        import math
        for k, v in ctx.items():
            assert math.isfinite(v), f"Non-finite value for key {k}: {v}"
