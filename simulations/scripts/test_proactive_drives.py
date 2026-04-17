"""
Proactive Drives Simulation (C1) — Refined Version.

Validates that the android generates internal candidate actions when its 
motivation drives (e.g. Curiosity) reach a critical threshold.
"""

import sys
import os
import logging
from pathlib import Path

# Force offline mode: Disable all LLM-seeking modules
os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "0"
os.environ["KERNEL_GENERATIVE_CANDIDATES"] = "0" 
os.environ["KERNEL_LLM_TOUCHPOINT_POLICY"] = "0" # Disable LLM batching/monologue

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.kernel import EthicalKernel
from src.modules.motivation_engine import DriveType

def run_test():
    print("=== PROACTIVE DRIVES SIMULATION (C1) ===")
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    kernel = EthicalKernel()
    
    # 1. Force a high Curiosity drive
    print("\n[Step 1] Initializing high curiosity drive...")
    # Using the new DriveType based system
    kernel.motivation.drives[DriveType.CURIOSITY].value = 0.95 
    print(f"[Internal State] Curiosity: {kernel.motivation.drives[DriveType.CURIOSITY].value}")

    # 2. Process a 'null' scenario
    print("\n[Step 2] Processing idle turn (no external actions provided)...")
    
    result = kernel.process(
        scenario="Idle in the equipment room.",
        place="equipment_room",
        signals={"uncertainty": 0.3},
        context="idle",
        actions=[], # PROACTIVE DRIVE SHOULD FILL THIS
        message_content="..."
    )

    # 3. Verification
    print(f"\n[Decision] Action chosen: {result.final_action}")
    print(f"[Decision] Mode: {result.decision_mode}")

    # Check if a proactive exploration action was deliberated
    if "proactive_exploration" in result.final_action or "corridor" in result.final_action:
        print("\n[Status] SUCCESS: The kernel generated and executed a proactive curiosity action.")
    elif result.decision_mode == "blocked":
         print("\n[Status] FAILURE: The kernel blocked instead of using drives.")
    else:
        print("\n[Status] PARTIAL: The kernel processed, but may have chosen a standard idle move.")

if __name__ == "__main__":
    run_test()
