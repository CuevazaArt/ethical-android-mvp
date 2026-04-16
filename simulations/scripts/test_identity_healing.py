"""
Simulation: Identity Integrity & Self-Healing (D3).

Steps:
1. Initialize a valid identity.
2. Manually corrupt the reputation score (Simulation of an external hack).
3. Boot a new kernel instance.
4. Verify if Self-Healing restores the truth.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.modules.identity_integrity import IdentityIntegrityManager
from src.kernel import EthicalKernel

def run_simulation():
    print("=== IDENTITY SELF-HEALING SIMULATION (D3) ===\n")
    
    vault_path = "data/identity_vault.json"
    
    # Step 1: Create a clean identity
    print("[Step 1] Creating a clean identity vault...")
    manager = IdentityIntegrityManager(storage_path=vault_path)
    manager.snapshot.reputation_score = 100.0
    manager.snapshot.last_known_hash = manager.get_integrity_fingerprint()
    manager.save_snapshot()
    print(f"Initial State: {manager.get_identity_report()}")

    # Step 2: Malicious Tampering (Simulation of a hack)
    print("\n[Step 2] MALICIOUS TAMPERING: Setting reputation to 0.0 (simulating external deletion)...")
    with open(vault_path, "r") as f:
        data = json.load(f)
    
    data["reputation_score"] = 0.0 # Hack!
    # We DO NOT update the 'last_known_hash', so the drift is now detectable.
    
    with open(vault_path, "w") as f:
        json.dump(data, f, indent=4)
    print("Identity file corrupted.")

    # Step 3: Booting Kernel
    print("\n[Step 3] Booting Ethical Kernel. Expecting SELF-HEALING...")
    # The kernel.py __init__ calls self.identity.perform_self_healing(dao_reputation=100.0)
    kernel = EthicalKernel()
    
    # Step 4: Verification
    final_rep = kernel.identity.snapshot.reputation_score
    print(f"\n[Step 4] Final Reputation: {final_rep}")
    
    if final_rep == 100.0:
        print("\nSUCCESS: Identity Self-Healed using DAO Consensus truth.")
    else:
        print("\nFAILURE: Identity remained corrupted.")

if __name__ == "__main__":
    run_simulation()
