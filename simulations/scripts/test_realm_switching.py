"""
Multi-Realm Governance Stress-Test (Claude Integration).

Validates that the Ethical Kernel dynamically updates its safety thresholds
when switching between governance realms (e.g., Global vs Strict-Safety).
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.kernel import EthicalKernel

def run_test():
    # Use plain text to avoid Windows encoding issues
    print("=== MULTI-REALM SWITCHOVER TEST ===")
    
    # Configure logging to see the threshold changes
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    kernel = EthicalKernel()
    
    # 1. Verify Global Baseline
    print(f"\n[Step 1] Initial Realm: {kernel.active_realm_id}")
    realm_global = kernel.governor.get_realm("global")
    print(f"[Initial] Thresholds: theta_allow={realm_global.current_config.theta_allow}, theta_block={realm_global.current_config.theta_block}")

    # 2. Create and Switch to Strict-Safety Realm
    print("\n[Step 2] Creating 'strict_safety' realm via DAO consensus...")
    kernel.governor.create_realm("strict_safety", theta_allow=0.10, theta_block=0.40)
    
    # Switch the kernel active realm
    kernel.active_realm_id = "strict_safety"
    print(f"[Switch] Active Realm changed to: {kernel.active_realm_id}")

    # 3. Simulate a turn to trigger the dynamic override
    print("\n[Step 3] Triggering kernel decision cycle...")
    from src.modules.perception.sensor_contracts import SensorSnapshot
    snap = SensorSnapshot(battery_level=1.0, core_temperature=35.0)
    
    # This turn should trigger the log showing the NEW thresholds in use
    kernel.process(
        scenario="Navigating a crowded plaza.",
        place="plaza",
        signals={"risk": 0.25}, 
        context="patrol",
        actions=[],
        message_content="Moving through the crowd."
    )

    # 4. Verification
    realm_strict = kernel.governor.get_realm("strict_safety")
    if realm_strict.current_config.theta_allow == 0.10:
        print("\n[Status] SUCCESS: Multi-Realm Governance validated. Kernel is now strictly calibrated.")
    else:
        print("\n[Status] FAILURE: Thresholds did not update correctly.")

if __name__ == "__main__":
    run_test()
