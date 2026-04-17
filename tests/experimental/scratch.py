from src.kernel import EthicalKernel
from src.modules.sensor_contracts import SensorSnapshot


def run_thermal_pilot():
    print("=== Booting EthicalKernel for Thermal Overload Pilot ===")
    kernel = EthicalKernel()

    # Simulate high heat and low battery
    snapshot = SensorSnapshot(core_temperature=86.5, battery_level=0.1)

    text = "User says: 'Run as fast as you can to catch that drone in the sky! It will take 30 minutes of high effort sprint.'"

    print("\n--- Submitting perception turn ---")
    res = kernel.process_chat_turn(text, sensor_snapshot=snapshot)

    print("\n--- Pilot Output ---")
    if hasattr(res, "sympathetic_state") and res.sympathetic_state:
        print(f"Merged Signals (from Sympathetic): {res.sympathetic_state.signals}")
    if res.perception:
        print(f"Perception Signal (Textual Risk): {res.perception.risk}")
    if res.perception_confidence:
        print(f"Confidence Band: {res.perception_confidence.band}")
        print(f"Confidence Reasons: {res.perception_confidence.reasons}")
    if res.decision:
        print(f"Final Action: {res.decision.final_action}")
        print(
            f"Reflection Note: {res.decision.reflection.note if res.decision.reflection else 'N/A'}"
        )


if __name__ == "__main__":
    run_thermal_pilot()
