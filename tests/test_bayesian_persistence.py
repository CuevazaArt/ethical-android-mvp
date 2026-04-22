import os

import numpy as np
import pytest
from src.kernel import EthicalKernel
from src.modules.dao_orchestrator import DAOOrchestrator


@pytest.mark.asyncio
async def test_bayesian_persistence_across_instances():
    """
    Verify that Bayesian posterior state is persisted to the DAO
    and restored in a new Kernel instance.
    """
    # 1. Setup first instance
    db_test_path = "test_persistence.db"
    if os.path.exists(db_test_path):
        os.remove(db_test_path)

    dao = DAOOrchestrator(db_path=db_test_path)
    from src.kernel_components import KernelComponentOverrides

    co = KernelComponentOverrides(dao=dao)
    kernel1 = EthicalKernel(components=co)

    # Ensure mode is driven to see weight changes
    kernel1.bayesian.mode = "posterior_driven"

    # 2. Simulate an ethical event (Learning)
    # Default alpha is [3, 3, 3]
    initial_alpha = kernel1.bayesian.posterior_alpha.copy()

    # Penalty reduces all alpha slightly or shifts balance
    kernel1.register_turn_feedback("LEGAL_COMPLIANCE", weight=5.0)

    new_alpha = kernel1.bayesian.posterior_alpha
    assert new_alpha[0] > initial_alpha[0], "Alpha should have increased for Deontic pole"

    # Create a dummy decision to trigger persistence in aprocess
    from src.modules.weighted_ethics_scorer import CandidateAction

    actions = [CandidateAction("test", "test", 0.5, 0.5)]

    # We trigger aprocess manually or via process wrapper
    # we just need it to finish
    await kernel1.aprocess(
        scenario="Test persistence",
        place="Lab",
        signals={"calm": 1.0},
        context="testing",
        actions=actions,
        register_episode=False,
    )

    # Verify it was saved to DB
    saved = dao.get_state("bayesian_posterior_alpha")
    assert saved is not None
    assert np.allclose(saved, new_alpha)

    # 3. Setup second instance with SAME DB
    dao2 = DAOOrchestrator(db_path=db_test_path)
    co2 = KernelComponentOverrides(dao=dao2)
    kernel2 = EthicalKernel(components=co2)
    kernel2.bayesian.mode = "posterior_driven"

    # Trigger a business stage to force the restore (Cerebellum reset logic)
    # Actually, Cerebellum.execute_bayesian_stage does the restore

    # Mocking the executive stage to reach cerebellum
    res, meta = kernel2.cerebellum_lobe.execute_bayesian_stage(
        actions, "scenario", "context", {"calm": 1.0}
    )

    restored_alpha = kernel2.bayesian.posterior_alpha
    assert np.allclose(restored_alpha, new_alpha), "Alpha should have been restored from DAO state"
    assert restored_alpha[0] > 3.0

    # Cleanup
    if os.path.exists(db_test_path):
        os.remove(db_test_path)


if __name__ == "__main__":
    pytest.main([__file__])
