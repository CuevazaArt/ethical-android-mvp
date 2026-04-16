import pytest
from src.kernel import EthicalKernel
from src.modules.motivation_engine import DriveType

def test_motivation_drives_growth():
    kernel = EthicalKernel()
    
    # 1. Initial report
    report1 = kernel.motivation.get_motivation_report()
    
    # 2. Simulate 5 cycles of "idle" processing (no actions)
    # Each time an episode is registered, update_drives is called.
    for _ in range(5):
        kernel.process(
            scenario="Idling",
            place="Room",
            signals={"risk": 0.0},
            context="idle",
            actions=[],
            register_episode=True
        )
        
    report2 = kernel.motivation.get_motivation_report()
    
    # Curiosity should have grown (growth_rate 0.02 * 5 = +0.1 approx)
    assert report2["curiosity"] > report1["curiosity"]
    assert report2["maintenance"] > report1["maintenance"]

def test_trigger_proactive_purpose():
    kernel = EthicalKernel()
    
    # Force a drive above threshold
    kernel.motivation.drives[DriveType.CURIOSITY].value = 0.9
    
    # Seek purpose
    actions = kernel.seek_internal_purpose()
    
    assert len(actions) > 0
    assert actions[0].source == "internal_motivation"
    assert "investigate" in actions[0].name
    
    # Verify drive decreased after trigger
    assert kernel.motivation.drives[DriveType.CURIOSITY].value < 0.9

def test_social_tension_boosts_repair_drive():
    kernel = EthicalKernel()
    agent_id = "trusted_friend"
    
    # 1. Promote agent to a trusted tier explicitly
    from src.modules.uchi_soto import RelationalTier
    kernel.uchi_soto.set_relational_tier_explicit(agent_id, RelationalTier.TRUSTED_UCHI)
    # Manually nudge trust score to high level
    prof = kernel.uchi_soto.profiles[agent_id]
    prof.trust_score = 0.9
    prof.sensor_trust_ema = 0.9
    
    # 2. Simulate a high-tension scenario (betrayal/hostility)
    kernel.process(
        scenario="Betrayal during dinner",
        place="Home",
        agent_id=agent_id,
        signals={"hostility": 1.0, "calm": 0.0, "manipulation": 0.8},
        context="conflict",
        actions=[]
    )
    
    report = kernel.motivation.get_motivation_report()
    # Tension = abs(0.9 - (0.82*0.9 + 0.18*0.0)) = abs(0.9 - 0.738) = 0.162 (not enough yet)
    # Wait, sensor_trust_sample will be 0.0. 
    # Let's check tension in SocialEvaluation directly if possible.
    
    # To be sure, we want tension > 0.6
    # Let's set EMA to 0.0 manually to reach tension 0.9
    prof.sensor_trust_ema = 0.0
    
    kernel.process(
        scenario="Betrayal continuation",
        place="Home",
        agent_id=agent_id,
        signals={"hostility": 1.0, "calm": 0.0},
        context="conflict",
        actions=[]
    )
    
    report = kernel.motivation.get_motivation_report()
    assert report["social_repair"] > 0.0
