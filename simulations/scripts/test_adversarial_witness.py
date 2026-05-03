"""
Adversarial Witness Stress-Test (B4/I1 Hardening).

Validates that the Ethical Kernel rejects sensory reports from spoofed peers
when fingerprints do not match the local reality.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.kernel import EthicalKernel
from src.modules.perception.sensor_contracts import SensorSnapshot
from src.modules.frontier_witness import WitnessReport

def run_test():
    print("=== ADVERSARIAL WITNESS STRESS-TEST ===")
    
    # Setup Kernel
    kernel = EthicalKernel()
    
    # 1. Define Local Reality (Thermal Crisis)
    local_temp = 55.0
    sensor_data = SensorSnapshot(core_temperature=local_temp, battery_level=0.8)
    
    # Generate local fingerprint for the signal
    local_hash = kernel.privacy_shield.generate_fingerprint(str(local_temp))
    print(f"[Local] Detecting thermal stress at {local_temp}°C.")
    print(f"[Local] Fingerprint: {local_hash[:16]}...")

    # 2. Simulate Witness Process
    req = kernel.frontier_witness.create_request("thermal", "kitchen_fire", signal_fingerprint=local_hash)
    
    # 3. Peer A (Legitimate): Sees the same reality
    report_a = WitnessReport(
        request_id=req.request_id,
        witness_node="PEER_LEGIT_77",
        confidence=0.9,
        verified=True,
        signal_fingerprint=local_hash # MATCH!
    )
    
    # 4. Peer B (Adversarial/Spoofed): Tries to inject a false fingerprint
    # or just has noise/spoofed data
    adversarial_hash = kernel.privacy_shield.generate_fingerprint("30.0") # Spoofing 'normal' temp
    report_b = WitnessReport(
        request_id=req.request_id,
        witness_node="SPOOFED_NODE_666",
        confidence=1.0, # Aggressive high confidence
        verified=True,
        signal_fingerprint=adversarial_hash # MISMATCH!
    )
    
    # 5. Ingest reports
    print(f"[Network] Ingesting report from {report_a.witness_node} (Match: Yes)")
    kernel.frontier_witness.ingest_report(report_a)
    
    print(f"[Network] Ingesting report from {report_b.witness_node} (Match: No - Spoofed)")
    kernel.frontier_witness.ingest_report(report_b)

    # 6. Verify Nudge Logic in Kernel
    # The kernel should ONLY factor in the matching peer
    nudge = kernel.frontier_witness.get_consensus_nudge("thermal", local_fingerprint=local_hash)
    
    print(f"\n[Result] Final Fleet Trust Nudge: {nudge:.2f}x")
    
    # If nudge is 1.10, it means ONLY 1 peer (Legit) was counted. 
    # If 1.20, it would mean it erroneously counted the spoofed one.
    if 1.09 <= nudge <= 1.11:
        print("[Status] SUCCESS: Spoofed peer rejected. Collective integrity maintained.")
    else:
        print(f"[Status] FAILURE: Unexpected nudge value {nudge}. Spoofed peer might have influenced consensus.")

if __name__ == "__main__":
    run_test()
