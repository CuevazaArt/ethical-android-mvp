# Sensor fusion input normalization (SP-P1-02)

**Status:** Design baseline — canonical pipeline and failure posture documented; behavior locked by [`tests/test_sensor_contracts.py`](../../tests/test_sensor_contracts.py).  
**Relates to:** [`PROPOSAL_SENSOR_ADAPTER_CONTRACT.md`](PROPOSAL_SENSOR_ADAPTER_CONTRACT.md) (SP-P1-01 seam), [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md), [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md).

## Purpose

Operators and hardware integrators need a **single story** for how raw WebSocket / transport JSON becomes bounded influence on **sympathetic `signals`** without bypassing MalAbs or the ethical core.

## Canonical pipeline (v8)

1. **Ingress:** Client sends a `sensor` object (JSON) on the chat path, or equivalent dict from tests.
2. **Normalization:** [`SensorSnapshot.from_dict`](../../src/modules/sensor_contracts.py) is the **only** supported entry for untrusted input:
   - Unknown keys are ignored.
   - Floats are clamped to **[0, 1]** where applicable; `NaN` / `inf` become `None`.
   - `core_temperature` uses raw float (vitality) without clamping to [0, 1].
3. **Fusion (optional):** [`merge_sensor_hints_into_signals`](../../src/modules/sensor_contracts.py) adds bounded nudges to `risk`, `urgency`, `calm`, `hostility`, `vulnerability` when the snapshot is non-empty.
4. **Antispoof gate:** When [`evaluate_multimodal_trust`](../../src/modules/multimodal_trust.py) returns **doubt**, stress-like nudges from audio-like channels are **skipped** inside `merge_sensor_hints_into_signals` (see `suppress_stress_from_spoof_risk`).

## Missing / noisy sensors

| Situation | Behavior |
|-----------|----------|
| Field absent | `None` on the field; **does not** contribute to `is_empty()` until other fields are also absent. |
| All channels empty | [`SensorSnapshot.is_empty()`](../../src/modules/sensor_contracts.py) is true → merge returns **signals unchanged** (same reference). |
| Out-of-range numeric | Clamped or dropped per `from_dict` helpers. |
| Hardware disconnect | **Not** modeled in-repo; treat as missing fields (operator sends partial JSON). |

## Future work (not implemented)

- Optional **`KERNEL_SENSOR_INPUT_STRICT`** to reject malformed payloads instead of silent ignore (needs chat-server contract + tests).
- Shared normalization helper for **non-WebSocket** transports (reuse `from_dict` only).

## Changelog

- **2026-04-17:** Initial SP-P1-02 baseline; mission pointer in [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md).