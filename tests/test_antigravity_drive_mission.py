from src.kernel import EthicalKernel
from src.modules.cognition.strategy_engine import MissionOrigin


def test_drive_arbiter_mission_intent():
    """
    Verifies that an active mission generates a 'Mission Advancement' intent in the DriveArbiter.
    """
    kernel = EthicalKernel()

    # 1. Create an active mission
    kernel.strategist.create_mission(
        title="Secure the perimeter", origin=MissionOrigin.OWNER, priority=0.9
    )

    # 2. Evaluate drives
    intents = kernel.drive_arbiter.evaluate(kernel)
    suggests = [i.suggest for i in intents]

    assert "advance_active_mission" in suggests
    mission_intent = next(i for i in intents if i.suggest == "advance_active_mission")
    assert "Secure the perimeter" in mission_intent.reason
    assert mission_intent.priority > 0.7


if __name__ == "__main__":
    pass
