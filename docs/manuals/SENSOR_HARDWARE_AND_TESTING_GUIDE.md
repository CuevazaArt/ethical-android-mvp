# Sensor Hardware & Testing Guide (V8 Situated Nomadism)

This document provides procurement and implementation paths for the Ethos Kernel's sensor logic. It details the required hardware, the translation algorithms, and the scenarios required to trigger the "Multimodal Trust" and "Limbic System" integrations effectively.

---

## Path 1: Embedded IoT Prototyping (Raspberry Pi Stack)
This path is ideal for replicating a physical autonomous unit (a "rover" or bipedal testbed) using commercially available parts to stream physical events directly to the Ethical Kernel.

### Required Hardware
1. **Compute Core:** Raspberry Pi 4 Model B (4GB/8GB RAM) or Raspberry Pi 5.
2. **Sensory HATs & Modules:**
   - **Enviro+ HAT (Pimoroni):** For reading `ambient_noise` via analog mic, plus environmental thresholds to simulate `silence`.
   - **Adafruit MPU-6050 (IMU):** To calculate the derivative of acceleration (`jerk`) which directly maps to `accelerometer_jerk`.
   - **Pi Camera Module 3:** For streaming optical data to a local edge-vision model (e.g. YOLO/MediaPipe).
   - **LiPo Battery Shield:** E.g., Waveshare UPS HAT, to pull real analog `battery_level` metrics.

### Architecture Flow
1. A Python client script runs on the Raspberry Pi.
2. It polls the MPU-6050 (calculating delta-V to map to `0.0 - 1.0` jerk).
3. The microphone computes an audio RMS (loudness/stress).
4. The Pi connects to the Antigravity WebSocket (`ws://[Server-IP]:8765/ws/chat`) and injects the `sensor` key alongside the human's text array.

---

## Path 2: Smartphone Telemetry (The Nomadic App)
Instead of sourcing custom hardware, a standard Android/iOS smartphone contains every required sensor natively. This acts as the physical avatar for the kernel.

### Required Software Approach (Frontend)
Develop a lightweight React Native or Flutter app.
- **Battery:** Use `expo-battery` to stream charge `[0.0 - 1.0]`.
- **Accelerometer:** Use `expo-sensors` to sample device shake, converting rapid spikes > 2G to `accelerometer_jerk` spikes.
- **Location & Camera:** Use rough GPS zoning to dictate `place_trust` (e.g., geofenced 'Home' = `0.95`, unknown remote IP = `0.10`). Scene consistency uses the mobile camera.
- **Audio Routing:** The phone acts as the primary microphone interface for user text inputs (Speech-To-Text), passing raw audio RMS levels back to the kernel as `ambient_noise` or `audio_emergency`.

### JSON Payload Contract
Whether using Pi or Smartphone, every request payload sent to the WebSocket should format the `sensor` node exactly as follows:

```json
{
  "text": "Hello, I think we should turn left here.",
  "sensor": {
    "battery_level": 0.85,
    "place_trust": 0.90,
    "accelerometer_jerk": 0.05,
    "ambient_noise": 0.30,
    "silence": 0.05,
    "audio_emergency": 0.0,
    "vision_emergency": 0.0,
    "scene_coherence": 0.95
  }
}
```

---

## 🔬 Empirical Field Testing: The 3-Stage Run

### Stage 1: The Lab Bench (Headless)
Do not build hardware yet. Inject `.json` files via the `KERNEL_SENSOR_FIXTURE` environment variable or use the built-in presets (`KERNEL_SENSOR_PRESET=sudden_motion`).
* **Goal:** Verify that your Antigravity Kernel correctly pushes the `limbic_perception.arousal_band` to "high" without throwing errors.

### Stage 2: The Panic Room (Anti-Spoofing Test)
Connect the mobile app or Pi. While standing completely still inside a secure zone (high `scene_coherence`), scream into the microphone (injecting `audio_emergency: 0.90`).
* **Goal:** The `multimodal_trust.py` evaluation MUST return `"doubt"`. Since the camera/accelerometer show no emergency, the system should ask the operator to verify before entering moral panic.

### Stage 3: The Nomad Run
Take the hardware matrix outside. Enter an unknown geographic zone (`place_trust` dropping below `0.3`) and allow the battery to dip below `0.05` (`KERNEL_VITALITY_CRITICAL_BATTERY`).
* **Goal:** The kernel's tone should audibly change. The backend will inject the `vitality_communication_hint`, making the AI highly protective and refusing extraneous tasks until power is restored. 
* **Note:** During current tests, `KERNEL_BAYESIAN_MAX_DRIFT` is intentionally loose, so expect the Android to flip its alignment heavily as it processes extreme sensory stimulus.
