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
    
    # Case 2: Parametric Sweep (Hardening Rule 2)
    print("\n--- Parametric Sensitivity Sweep ---")
    results = []
    for m in np.linspace(0.0, 5.0, 11): # Up to 5.0 to check saturation
        res = await limbic.execute_stage_async(
            agent_id="User1",
            signals=signals.copy(),
            message_content=f"Test sweep magnitude {m}",
            turn_index=1,
            trauma_magnitude=m
        )
        val = res.social_evaluation.relational_tension
        results.append((m, val))
        status = "OK" if np.isfinite(val) else "UNSTABLE (NaN/Inf)"
        print(f"Trauma {m:0.1f} -> Tension: {val:.4f} [{status}]")

    # Anti-NaN verification for tests
    all_finite = np.all([np.isfinite(v[1]) for v in results])
    if all_finite:
        print("\n[SUCCESS] Trauma curve is mathematically stable (Anti-NaN Verified).")
    else:
        print("\n[CRITICAL] Trauma curve detected non-finite values!")

if __name__ == "__main__":
    asyncio.run(test_trauma_sensitivity())
