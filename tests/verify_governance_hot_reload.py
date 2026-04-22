import asyncio
import os
from pathlib import Path

import src.modules.safety.semantic_chat_gate as sem_gate
from src.kernel import EthicalKernel


async def verify_governance_hot_reload():
    import sys

    print(f"DEBUG: sys.path: {sys.path}")
    import src.kernel

    print(f"DEBUG: src.kernel file: {src.kernel.__file__}")
    print("Initializing Kernel with Multi-Realm Governance enabled...")
    os.environ["KERNEL_MULTI_REALM_GOVERNANCE_ENABLED"] = "1"
    os.environ["KERNEL_EVENT_BUS"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    # Ensure artifacts path is clean
    artifacts_path = Path("artifacts/test_realms")
    if artifacts_path.exists():
        import shutil

        shutil.rmtree(artifacts_path)
    os.environ["KERNEL_MULTI_REALM_ARTIFACTS_PATH"] = str(artifacts_path)

    kernel = EthicalKernel()

    # Check initial thresholds in sem_gate
    initial_allow = sem_gate._allow_threshold()
    initial_block = sem_gate._block_threshold()
    print(f"Initial sem_gate thresholds: allow={initial_allow}, block={initial_block}")

    # Create a realm and a proposal
    governor = kernel.governor
    realm_id = "test_realm"
    governor.create_realm(realm_id, theta_allow=0.45, theta_block=0.82)

    new_allow = 0.55
    new_block = 0.90
    print(f"Proposing new thresholds: allow={new_allow}, block={new_block}")

    proposal = governor.propose_threshold_update(
        realm_id=realm_id,
        proposer_id="admin",
        theta_allow=new_allow,
        theta_block=new_block,
        reasoning="Test hot-reload",
    )

    # Cast vote and resolve
    governor.cast_vote(realm_id, proposal.proposal_id, "voter1", vote_weight=1.0, vote_for=True)
    success = governor.resolve_proposal(realm_id, proposal.proposal_id)

    if success:
        print("Proposal executed successfully.")
        # Wait a bit for async event if any (though currently it's synchronous in event_bus)
        await asyncio.sleep(0.1)

        # Check if sem_gate thresholds were updated
        updated_allow = sem_gate._allow_threshold()
        updated_block = sem_gate._block_threshold()
        print(f"Updated sem_gate thresholds: allow={updated_allow}, block={updated_block}")

        if abs(updated_allow - new_allow) < 1e-6 and abs(updated_block - new_block) < 1e-6:
            print("SUCCESS: Hot-reload verified.")
        else:
            print("FAILURE: Thresholds did not update as expected.")
    else:
        print("FAILURE: Proposal resolution failed.")

    # Cleanup
    if artifacts_path.exists():
        import shutil

        shutil.rmtree(artifacts_path)


if __name__ == "__main__":
    asyncio.run(verify_governance_hot_reload())
