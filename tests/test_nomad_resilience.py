import asyncio
import pytest
import time
from src.kernel_lobes.perception_lobe import PerceptiveLobe
from src.modules.nomad_bridge import get_nomad_bridge

@pytest.mark.asyncio
async def test_somatic_inertia_ghosting():
    """
    Verifies that the PerceptiveLobe correctly enters Somatic Inertia 
    and 'ghosts' sensory impulses when the Nomad vessel disconnects.
    """
    # 1. Setup bridge in 'healthy' state
    bridge = get_nomad_bridge()
    bridge._last_sensor_update = time.time()
    bridge._is_vessel_healthy = True
    
    # 2. Setup Perceptive Lobe (Mock dependencies)
    from unittest.mock import MagicMock
    lobe = PerceptiveLobe(
        safety_interlock=MagicMock(),
        strategist=MagicMock(),
        llm=MagicMock(),
        somatic_store=MagicMock(),
        buffer=MagicMock(),
        buffer_long=MagicMock(),
        absolute_evil=MagicMock(),
        subjective_clock=MagicMock(turn_index=1),
        thalamus=MagicMock(),
        vision_engine=None
    )
    
    # 3. Verify healthy state
    impulses = lobe.get_sensory_impulses()
    assert impulses["offline"] is False
    assert impulses["inertia_active"] is False
    
    # 4. Simulate DISCONNECTION (Stale data > 5s)
    bridge._last_sensor_update = time.time() - 10.0
    
    # 5. First check: Should enter inertia (ghosting)
    impulses_ghost = lobe.get_sensory_impulses()
    assert impulses_ghost["offline"] is True
    assert impulses_ghost["inertia_active"] is True
    assert "sensory_shutdown" not in impulses_ghost
    
    print("✅ Somatic Inertia active (Ghosting impulses...)")
    
    # 6. Wait for inertia to expire (> 5s from current time)
    # We cheat the clock slightly in the lobe
    lobe._shutdown_deadline = time.time() - 1.0
    
    # 7. Final check: Should shutdown
    impulses_shutdown = lobe.get_sensory_impulses()
    assert impulses_shutdown.get("sensory_shutdown") is True
    assert impulses_shutdown["offline"] is True
    
    print("✅ Sensory Shutdown triggered after inertia expiry.")

if __name__ == "__main__":
    asyncio.run(test_somatic_inertia_ghosting())
