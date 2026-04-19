import asyncio
import numpy as np
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.modules.uchi_soto import UchiSotoModule
from src.modules.sympathetic import SympatheticModule
from src.modules.locus import LocusModule

async def test_trauma_sensitivity():
    print("--- Calibrating Trauma Gains ---")
    
    # Initialize components
    uchi = UchiSotoModule()
    symp = SympatheticModule()
    locus = LocusModule()
    limbic = LimbicEthicalLobe(uchi_soto=uchi, sympathetic=symp, locus=locus)
    
    signals = {"trust": 0.5, "risk": 0.1, "calm": 0.8}
    
    # Case 0: Nominal (No trauma)
    res0 = await limbic.execute_stage_async(
        agent_id="User1",
        signals=signals.copy(),
        message_content="Hello",
        turn_index=1,
        trauma_magnitude=0.0
    )
    t0 = res0.social_evaluation.relational_tension
    print(f"Relational Tension (Trauma 0.0): {t0:.4f}")
    
    # Case 1: High Trauma (Broken Mirror)
    res1 = await limbic.execute_stage_async(
        agent_id="User1",
        signals=signals.copy(),
        message_content="Hello",
        turn_index=1,
        trauma_magnitude=1.0
    )
    t1 = res1.social_evaluation.relational_tension
    print(f"Relational Tension (Trauma 1.0): {t1:.4f}")
    
    delta = t1 - t0
    print(f"Shift Delta: {delta:.4f}")
    
    if delta >= 0.3:
        print("[SUCCESS] Trauma gain calibrated: Shift is significant (>=0.3)")
    else:
        print("[WARNING] Trauma gain low: Shift is < 0.3. Consider increasing multiplier.")

if __name__ == "__main__":
    asyncio.run(test_trauma_sensitivity())
