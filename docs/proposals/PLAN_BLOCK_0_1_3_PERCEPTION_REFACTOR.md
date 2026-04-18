# Implementation Plan: Block 0.1.3 - Desmonolithization of Perceptive Logic

## Objective
Migrate all perception-related logic and state handling from the 2400+ line `src/kernel.py` monolithic `EthicalKernel` class into the `src/kernel_lobes/perception_lobe.py` module. This improves maintainability and prepares for pure Async I/O (Task 0.1.1).

## Impacted Files
- `src/kernel.py`: Remove perception/sensor-stack helper methods and redirect calls to the lobe.
- `src/kernel_lobes/perception_lobe.py`: Receive the migrated logic.
- `src/kernel_lobes/models.py`: Update data models if necessary for cross-lobe communication.

## Step-by-Step Migration

### Phase 1: Preparation of PerceptiveLobe
1.  **Move Imports**: Ensure `PerceptiveLobe` has all necessary imports from `EthicalKernel` (e.g., `SensorSnapshot`, `LLMPerception`, etc.).
2.  **State Injection**: Ensure `PerceptiveLobe` has access to necessary sub-modules (e.g., `uchi_soto`, `user_model`, `somatic_store`).
    > [!NOTE]
    > To avoid circular dependencies, we might need to pass specialized context objects or initialize the Lobe with these components.

### Phase 2: Logic Transfer
1.  **Observability Preprocessing**: Move `_preprocess_text_observability` to the lobe.
2.  **Support Buffer Logic**: Move `_build_support_buffer_snapshot` and `_support_buffer_context_line`.
3.  **Sensor Stack Assessment**: Move `_chat_assess_sensor_stack`.
4.  **Limbic Profile Building**: Move `_build_limbic_perception_profile`.
5.  **Perception Core Methods**: Move `_run_perception_stage` and `_run_perception_stage_async`.

### Phase 3: Integration in EthicalKernel
1.  **Redirect Entry Points**: Update `process_chat_turn_async` and `aprocess_natural` to call `self.perceptive_lobe.run_stage_async(...)`.
2.  **Clean Up**: Delete the old private methods in `EthicalKernel`.

## Verification Plan
1.  **Unit Tests**: Run `tests/test_ethical_properties.py`.
2.  **Vertical Tests**: Run `python scripts/eval/run_llm_vertical_tests.py`.
3.  **Pilot Simulation**: Run `python scripts/run_empirical_pilot.py` to ensure decision parity.
