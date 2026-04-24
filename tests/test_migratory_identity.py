"""
Tests for Block 4.3: Identidad Migratoria e Interoperabilidad (C5).
"""

from src.kernel import EthicalKernel
from src.modules.ethics.weighted_ethics_scorer import CandidateAction
from src.modules.memory.narrative_types import HardwareProfile
from src.persistence.kernel_io import apply_snapshot, extract_snapshot


def test_hardware_migration_preserves_narrative():
    kernel = EthicalKernel(llm_mode="local")

    # Initial state: Android body
    assert kernel.migration.current_body.hardware_profile == HardwareProfile.ANDROID

    # 1. Register episode with Android
    kernel.process(
        scenario="helping in the street",
        place="city",
        signals={"trust": 0.8},
        context="everyday",
        actions=[CandidateAction("help", "help", 0.5)],
    )

    ep1 = kernel.memory.episodes[-1]
    assert ep1.body_state.hardware_profile == HardwareProfile.ANDROID
    assert "vision" in ep1.body_state.capabilities

    # 2. Migrate to Drone body
    kernel.migration.migrate_to(HardwareProfile.DRONE, "drone_alpha_9")
    assert kernel.migration.current_body.hardware_profile == HardwareProfile.DRONE
    assert kernel.migration.current_body.hardware_id == "drone_alpha_9"

    # 3. Register episode with Drone
    kernel.process(
        scenario="aerial surveillance of hazard",
        place="forest",
        signals={"risk": 0.6},
        context="emergency",
        actions=[CandidateAction("report", "report", 0.7)],
    )

    ep2 = kernel.memory.episodes[-1]
    assert ep2.body_state.hardware_profile == HardwareProfile.DRONE
    assert "vision_ir" in ep2.body_state.capabilities

    # 4. Verify narrative continuity
    assert len(kernel.memory.episodes) == 2
    assert kernel.memory.episodes[0].body_state.hardware_profile == HardwareProfile.ANDROID
    assert kernel.memory.episodes[1].body_state.hardware_profile == HardwareProfile.DRONE


def test_snapshot_persistence_handles_body_migration():
    kernel = EthicalKernel(llm_mode="local")

    # Migrate to Mobile form
    kernel.migration.migrate_to(HardwareProfile.MOBILE, "user_phone_x")

    # Extract
    snap = extract_snapshot(kernel)
    assert snap.migratory_body["hardware_profile"] == "mobile"
    assert "gps" in snap.migratory_body["capabilities"]

    # Restore into a new kernel
    kernel_new = EthicalKernel(llm_mode="local")
    apply_snapshot(kernel_new, snap)

    assert kernel_new.migration.current_body.hardware_profile == HardwareProfile.MOBILE
    assert kernel_new.migration.current_body.hardware_id == "user_phone_x"
    assert "gps" in kernel_new.migration.current_body.capabilities
