# Perception Hardware Unblock Actions (105.4)

Use this checklist to move `preflight_ready` from `false` to `true` before re-running pilot gate `105.3`.

## 1) Physical connection sanity (2-3 min)

- Connect one USB microphone directly (avoid passive hubs).
- Connect one UVC webcam directly (USB 3.x preferred).
- Keep one stable audio output endpoint connected (wired headset preferred).
- Disconnect duplicate/unused capture peripherals to reduce driver ambiguity.

## 2) Windows device verification (3-5 min)

Run:

```powershell
python scripts/eval/perception_hardware_preflight.py
```

Pass condition:

- `camera_count >= 1`
- `microphone_count >= 1`
- `audio_endpoint_count >= 1`
- `preflight_ready = true`

If still blocked:

- Open `Device Manager` and confirm camera appears under `Cameras` or `Imaging devices`.
- Confirm microphone appears as an input-capable audio endpoint.
- Re-seat USB cable and retry preflight.

## 3) Driver and permission recovery (5-8 min)

- In `Settings -> Privacy & security -> Camera`, enable camera access.
- In `Settings -> Privacy & security -> Microphone`, enable microphone access.
- Update/reinstall device driver only for missing class (`camera` or `microphone`), then rerun preflight.

## 4) Pilot rerun gate execution (2-3 min)

After preflight is green:

```powershell
python scripts/eval/perception_pilot_rerun_gate.py --require-pass
```

Pass condition:

- report shows `status = PASS`
- report shows `gate_pass = true`

## 5) If rerun gate remains BLOCKED

- Keep last `PERCEPTION_HARDWARE_PREFLIGHT.json` and `PERCEPTION_PILOT_RERUN_GATE_REPORT.json`.
- Record blocker in pilot evidence incidents using taxonomy from `104.2` (`capture_disconnect`, `rollback_failure`, etc.).
- Escalate only with concrete artifact paths and current command outputs.
