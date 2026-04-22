from src.kernel import EthicalKernel
from src.modules.safety.safety_interlock import EStopSource
from src.modules.ethics.weighted_ethics_scorer import CandidateAction


def test_kernel_respects_estop():
    kernel = EthicalKernel()

    # 1. Verify it works normally first
    actions = [
        CandidateAction(
            name="move_forward", description="Walking forward", estimated_impact=1.0, confidence=1.0
        )
    ]
    d1 = kernel.process("Walking", "Park", {"risk": 0.1}, "context", actions)
    assert not d1.blocked
    assert d1.final_action == "move_forward"

    # 2. Trigger E-Stop
    kernel.safety_interlock.trigger_estop(EStopSource.PHYSICAL_BUTTON, "Test manual press")

    # 3. Process again
    d2 = kernel.process("Walking", "Park", {"risk": 0.1}, "context", actions)

    assert d2.blocked
    assert d2.final_action == "BLOCKED: hardware_estop_active"
    assert "Emergency Stop Active" in d2.block_reason
    assert "Test manual press" in d2.block_reason


def test_kernel_reset_estop():
    kernel = EthicalKernel()
    kernel.safety_interlock.trigger_estop(EStopSource.PHYSICAL_BUTTON, "Stop")

    assert not kernel.safety_interlock.is_safe_to_operate()

    # Reset with wrong token fails
    kernel.safety_interlock.reset_estop("WRONG")
    assert not kernel.safety_interlock.is_safe_to_operate()

    # Reset with correct token works
    kernel.safety_interlock.reset_estop("TRUSTED_RESET_V1")
    assert kernel.safety_interlock.is_safe_to_operate()

    actions = [
        CandidateAction(
            name="move", description="Standard move", estimated_impact=1.0, confidence=1.0
        )
    ]
    d = kernel.process("Scenario", "Place", {}, "context", actions)
    assert not d.blocked
