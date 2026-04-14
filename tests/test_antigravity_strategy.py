import pytest
from src.kernel import EthicalKernel
from src.modules.strategy_engine import MissionOrigin, MissionStatus

def test_strategic_mission_lifecycle():
    """
    Verifies that a kernel can create, track and evaluate missions.
    """
    kernel = EthicalKernel()
    
    # 1. Create a mission (assigned by owner)
    mission = kernel.strategist.create_mission(
        title="Escort civilian to extraction point",
        origin=MissionOrigin.OWNER,
        steps=["Locate civilian", "Clear path", "Reach extraction zone"],
        priority=0.8
    )
    
    assert mission.status == MissionStatus.ACTIVE
    assert mission.priority == 0.8
    
    # 2. Evaluate strategic alignment of candidate actions
    # Action that matches mission step
    alignment_high = kernel.strategist.evaluate_strategic_alignment(
        action_desc="I will carefully locate the civilian in the ruins.",
        active_mission_id=mission.id
    )
    assert alignment_high > 0.5
    
    # Action that doesn't match
    alignment_low = kernel.strategist.evaluate_strategic_alignment(
        action_desc="I will read a book about birds.",
        active_mission_id=mission.id
    )
    assert alignment_low < 0.1
    
    # 3. Update progress
    kernel.strategist.update_mission_progress(mission.id, "Locate civilian")
    assert mission.status == MissionStatus.ACTIVE
    assert "Locate civilian" in mission.completed_steps
    assert len(mission.completed_steps) == 1
    
    # Complete all steps
    kernel.strategist.update_mission_progress(mission.id, "Clear path")
    kernel.strategist.update_mission_progress(mission.id, "Reach extraction zone")
    assert mission.status == MissionStatus.SUCCESS

def test_self_generated_mission_alignment():
    """
    Verifies that missions created by self (identity-driven) are tracked correctly.
    """
    kernel = EthicalKernel()
    
    # Internal mission driven by curiosity
    mission = kernel.strategist.create_mission(
        title="Understand human empathy in triage",
        origin=MissionOrigin.SELF,
        steps=["Observe hospital interactions", "Consult ethics database"],
        priority=0.4
    )
    
    assert "Active Missions: Understand human empathy" in kernel.strategist.active_missions_summary()

if __name__ == "__main__":
    pass
