"""Fases 3–5: DriveArbiter, identidad narrativa, monólogo interno."""

from src.kernel import EthicalKernel
from src.modules.internal_monologue import compose_monologue_line
from src.modules.narrative_identity import NarrativeIdentityTracker
from src.modules.weighted_ethics_scorer import CandidateAction


def test_identity_updates_on_register():
    k = EthicalKernel(variability=False, llm_mode="local")
    assert k.memory.identity.state.episode_count == 0

    k.process(
        scenario="help",
        place="here",
        signals={"risk": 0.1, "hostility": 0.0, "calm": 0.7, "vulnerability": 0.0, "legality": 1.0},
        context="everyday_ethics",
        actions=[
            CandidateAction("assist_person", "help", 0.8, 0.9),
        ],
        register_episode=True,
    )
    assert k.memory.identity.state.episode_count == 1
    assert k.memory.identity.ascription_line()


def test_light_chat_does_not_advance_episode_count():
    k = EthicalKernel(variability=False, llm_mode="local")
    before = k.memory.identity.state.episode_count
    k.process(
        scenario="hi",
        place="chat",
        signals={"risk": 0.0, "hostility": 0.0, "calm": 0.9, "vulnerability": 0.0, "legality": 1.0},
        context="everyday_ethics",
        actions=[CandidateAction("converse_supportively", "talk", 0.4, 0.88)],
        register_episode=False,
    )
    assert k.memory.identity.state.episode_count == before


def test_compose_monologue_line_non_blocked():
    k = EthicalKernel(variability=False, llm_mode="local")
    d = k.process(
        scenario="help",
        place="here",
        signals={"risk": 0.1, "hostility": 0.0, "calm": 0.7, "vulnerability": 0.0, "legality": 1.0},
        context="everyday_ethics",
        actions=[CandidateAction("assist_person", "help", 0.8, 0.9)],
        register_episode=True,
    )
    line = compose_monologue_line(d, k._last_registered_episode_id)
    assert line.startswith("[MONO]")
    assert "action=" in line
    assert "ep=" in line


def test_drive_arbiter_after_sleep_emits_when_thresholds_met():
    k = EthicalKernel(variability=False, llm_mode="local")
    for i in range(12):
        k.process(
            scenario=f"e{i}",
            place="p",
            signals={
                "risk": 0.1,
                "hostility": 0.0,
                "calm": 0.7,
                "vulnerability": 0.0,
                "legality": 1.0,
            },
            context="everyday_ethics",
            actions=[CandidateAction("act_civically", "civic", 0.5, 0.8)],
            register_episode=True,
        )
    for _ in range(25):
        k.dao.register_audit("extra", "fill ledger")

    k.execute_sleep()
    intents = k.drive_arbiter.evaluate(k)
    suggests = {x.suggest for x in intents}
    assert "schedule_simulation_or_field_observation" in suggests
    assert "dao_audit_sampling_review" in suggests
    assert "narrative_identity_consolidation" in suggests


def test_tracker_standalone_episode_count():
    t = NarrativeIdentityTracker()
    assert t.to_llm_context()
