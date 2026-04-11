"""Kernel snapshot extract/apply and JSON file persistence (Phase 2)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.kernel import EthicalKernel
from src.persistence import (
    SCHEMA_VERSION,
    JsonFilePersistence,
    SqlitePersistence,
    apply_snapshot,
    extract_snapshot,
)
from src.modules.moral_hub import add_constitution_draft
from src.persistence.json_store import snapshot_from_dict
from src.simulations.runner import ALL_SIMULATIONS


def test_schema_version_constant():
    assert SCHEMA_VERSION == 3


def test_snapshot_from_dict_rejects_bad_version():
    with pytest.raises(ValueError, match="schema_version"):
        snapshot_from_dict({"schema_version": 0})
    with pytest.raises(ValueError, match="schema_version"):
        snapshot_from_dict({"schema_version": 99})


def test_snapshot_from_dict_migrates_v1():
    snap = snapshot_from_dict({"schema_version": 1})
    assert snap.schema_version == SCHEMA_VERSION
    assert snap.constitution_l1_drafts == []
    assert snap.constitution_l2_drafts == []
    assert snap.dao_proposals == []
    assert snap.dao_participants == []
    assert snap.dao_proposal_counter == 0


def test_snapshot_from_dict_migrates_v2():
    snap = snapshot_from_dict({"schema_version": 2, "constitution_l1_drafts": [{"id": "x"}]})
    assert snap.schema_version == SCHEMA_VERSION
    assert snap.dao_proposals == []


def test_constitution_drafts_roundtrip():
    k1 = EthicalKernel(variability=False)
    add_constitution_draft(k1, 1, "Coexistence draft", "Body A", proposer="tester")
    add_constitution_draft(k1, 2, "Owner note", "Body B")

    snap = extract_snapshot(k1)
    assert len(snap.constitution_l1_drafts) == 1
    assert len(snap.constitution_l2_drafts) == 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
    assert k2.constitution_l1_drafts == k1.constitution_l1_drafts
    assert k2.constitution_l2_drafts == k1.constitution_l2_drafts


def test_escalation_session_roundtrip():
    k1 = EthicalKernel(variability=False)
    k1.escalation_session.strikes = 4
    k1.escalation_session.idle_turns = 1

    snap = extract_snapshot(k1)
    assert snap.escalation_session_strikes == 4
    assert snap.escalation_session_idle_turns == 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
    assert k2.escalation_session.strikes == 4
    assert k2.escalation_session.idle_turns == 1


def test_user_model_and_subjective_clock_roundtrip():
    from src.modules.llm_layer import LLMPerception

    k1 = EthicalKernel(variability=False)
    k1.user_model.frustration_streak = 5
    k1.user_model.premise_concern_streak = 3
    k1.user_model.last_circle = "trusted_uchi"
    k1.user_model.turns_observed = 12
    k1.subjective_clock.turn_index = 7
    k1.subjective_clock.stimulus_ema = 0.41
    # Ensure tick-shaped path does not overwrite (we set fields directly as checkpoint would)
    p = LLMPerception(
        risk=0.2,
        urgency=0.2,
        hostility=0.1,
        calm=0.6,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.1,
        familiarity=0.5,
        suggested_context="everyday_ethics",
        summary="x",
    )
    k1.subjective_clock.tick(p)

    snap = extract_snapshot(k1)
    assert snap.user_model_last_circle == "trusted_uchi"
    assert snap.subjective_turn_index == 8
    assert abs(snap.subjective_stimulus_ema - k1.subjective_clock.stimulus_ema) < 1e-6

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
    assert k2.user_model.frustration_streak == k1.user_model.frustration_streak
    assert k2.user_model.premise_concern_streak == k1.user_model.premise_concern_streak
    assert k2.user_model.last_circle == k1.user_model.last_circle
    assert k2.user_model.turns_observed == k1.user_model.turns_observed
    assert k2.subjective_clock.turn_index == k1.subjective_clock.turn_index
    assert abs(k2.subjective_clock.stimulus_ema - k1.subjective_clock.stimulus_ema) < 1e-5


def test_metaplan_somatic_skills_roundtrip():
    from src.modules.sensor_contracts import SensorSnapshot

    k1 = EthicalKernel(variability=False)
    k1.metaplan.add_goal("Long project", 0.72)
    ss = SensorSnapshot(
        audio_emergency=0.85,
        place_trust=0.4,
        accelerometer_jerk=0.2,
    )
    k1.somatic_store.learn_negative_pattern(ss, weight=0.7)
    k1.skill_learning.request_ticket("export API", "needed for continuity demo")

    snap = extract_snapshot(k1)
    assert len(snap.metaplan_goals) >= 1
    assert snap.somatic_marker_weights
    assert len(snap.skill_learning_tickets) >= 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)
    assert len(k2.metaplan.goals()) == len(k1.metaplan.goals())
    assert k2.metaplan.goals()[0].title == k1.metaplan.goals()[0].title
    assert k2.somatic_store._negative_weights == k1.somatic_store._negative_weights
    assert len(k2.skill_learning._tickets) == len(k1.skill_learning._tickets)


def _kernel_with_metaplan_somatic_skills():
    from src.modules.sensor_contracts import SensorSnapshot

    k = EthicalKernel(variability=False)
    k.metaplan.add_goal("Long project", 0.72)
    ss = SensorSnapshot(
        audio_emergency=0.85,
        place_trust=0.4,
        accelerometer_jerk=0.2,
    )
    k.somatic_store.learn_negative_pattern(ss, weight=0.7)
    k.skill_learning.request_ticket("export API", "needed for continuity demo")
    return k


def test_json_file_metaplan_somatic_skills_roundtrip(tmp_path):
    k1 = _kernel_with_metaplan_somatic_skills()
    path = tmp_path / "checkpoint.json"
    store = JsonFilePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.metaplan.goals()) == len(k1.metaplan.goals())
    assert k2.metaplan.goals()[0].title == k1.metaplan.goals()[0].title
    assert k2.metaplan.goals()[0].id == k1.metaplan.goals()[0].id
    assert k2.somatic_store._negative_weights == k1.somatic_store._negative_weights
    assert len(k2.skill_learning._tickets) == len(k1.skill_learning._tickets)
    assert k2.skill_learning._tickets[0].id == k1.skill_learning._tickets[0].id


def test_sqlite_metaplan_somatic_skills_roundtrip(tmp_path):
    k1 = _kernel_with_metaplan_somatic_skills()
    path = tmp_path / "checkpoint.db"
    store = SqlitePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert k2.metaplan.goals()[0].title == k1.metaplan.goals()[0].title
    assert k2.somatic_store._negative_weights == k1.somatic_store._negative_weights
    assert k2.skill_learning._tickets[0].scope_description == k1.skill_learning._tickets[0].scope_description


def test_extract_apply_roundtrip_in_memory():
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[1]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    snap = extract_snapshot(k1)
    assert snap.schema_version == SCHEMA_VERSION
    assert len(snap.episodes) == 1

    k2 = EthicalKernel(variability=False)
    apply_snapshot(k2, snap)

    assert len(k2.memory.episodes) == len(k1.memory.episodes)
    assert k2.memory.episodes[0].id == k1.memory.episodes[0].id
    assert k2.memory.episodes[0].verdict == k1.memory.episodes[0].verdict
    assert k2.memory.identity.state.episode_count == k1.memory.identity.state.episode_count
    assert k2.bayesian.pruning_threshold == k1.bayesian.pruning_threshold
    assert len(k2.dao.records) == len(k1.dao.records)


def test_json_file_roundtrip(tmp_path):
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    path = tmp_path / "checkpoint.json"
    store = JsonFilePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.memory.episodes) == 1
    assert k2.memory.episodes[0].action_taken == k1.memory.episodes[0].action_taken


def test_load_missing_file(tmp_path):
    store = JsonFilePersistence(tmp_path / "missing.json")
    assert store.load() is None
    k = EthicalKernel(variability=False)
    assert store.load_into_kernel(k) is False
    assert len(k.memory.episodes) == 0


def test_sqlite_roundtrip(tmp_path):
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    path = tmp_path / "checkpoint.db"
    store = SqlitePersistence(path)
    store.save(extract_snapshot(k1))
    assert path.is_file()

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.memory.episodes) == 1
    assert k2.memory.episodes[0].action_taken == k1.memory.episodes[0].action_taken


def test_sqlite_load_missing_file(tmp_path):
    store = SqlitePersistence(tmp_path / "missing.db")
    assert store.load() is None
    k = EthicalKernel(variability=False)
    assert store.load_into_kernel(k) is False


def test_double_roundtrip_stable(tmp_path):
    """Save → load → extract again should match first snapshot (structural)."""
    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[3]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    s1 = extract_snapshot(k1)
    store = JsonFilePersistence(tmp_path / "c.json")
    store.save(s1)

    k2 = EthicalKernel(variability=False)
    store.load_into_kernel(k2)
    s2 = extract_snapshot(k2)

    assert s2.narrative_counter == s1.narrative_counter
    assert len(s2.episodes) == len(s1.episodes)
    assert s2.identity_state == s1.identity_state
    assert s2.dao_record_counter == s1.dao_record_counter


def test_json_file_encrypted_roundtrip(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    monkeypatch.setenv("KERNEL_CHECKPOINT_FERNET_KEY", key.decode())

    k1 = EthicalKernel(variability=False)
    scn = ALL_SIMULATIONS[2]()
    k1.process(scn.name, scn.place, scn.signals, scn.context, scn.actions)

    path = tmp_path / "checkpoint.enc.json"
    store = JsonFilePersistence(path)
    store.save(extract_snapshot(k1))
    blob = path.read_bytes()
    assert not blob.lstrip().startswith(b"{")

    k2 = EthicalKernel(variability=False)
    assert store.load_into_kernel(k2) is True
    assert len(k2.memory.episodes) == len(k1.memory.episodes)


def test_json_encrypted_load_fallback_plain_file(tmp_path, monkeypatch):
    """Plain JSON on disk + FERNET key set: decrypt fails, UTF-8 fallback loads."""
    from cryptography.fernet import Fernet

    k1 = EthicalKernel(variability=False)
    path = tmp_path / "legacy.json"
    JsonFilePersistence(path).save(extract_snapshot(k1))
    monkeypatch.setenv("KERNEL_CHECKPOINT_FERNET_KEY", Fernet.generate_key().decode())
    snap = JsonFilePersistence(path).load()
    assert snap is not None
    assert snap.schema_version == SCHEMA_VERSION
