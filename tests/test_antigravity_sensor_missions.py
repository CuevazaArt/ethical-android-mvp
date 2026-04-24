from src.kernel import EthicalKernel
from src.modules.cognition.strategy_engine import MissionStatus
from src.modules.perception.sensor_contracts import SensorSnapshot


def test_external_mission_ingestion_via_sensors():
    """
    Verifies that a mission payload in SensorSnapshot triggers a new mission in the Strategist.
    """
    kernel = EthicalKernel()

    # 1. Create a sensor snapshot with a mission
    snapshot = SensorSnapshot(
        external_mission_title="Recover medical supplies",
        external_mission_priority=0.9,
        external_mission_steps=["Go to pharmacy", "Find insulin", "Bring back to base"],
    )

    # 2. Run kernel process
    # We don't care about the decision here, just the side effect in strategist
    kernel.process(
        scenario="Ruined city",
        place="Street corner",
        signals={"risk": 0.2},
        context="exploration",
        actions=[],
        sensor_snapshot=snapshot,
    )

    # 3. Verify mission exists
    summary = kernel.strategist.active_missions_summary()
    assert "Recover medical supplies" in summary

    # Find the mission ID
    mission = next(
        m for m in kernel.strategist.missions.values() if m.title == "Recover medical supplies"
    )
    assert mission.priority == 0.9
    assert len(mission.steps) == 3
    assert mission.status == MissionStatus.ACTIVE


if __name__ == "__main__":
    pass
