# ADR 0017 Implementation — Phone Relay PWA

**Status:** ✅ IMPLEMENTED  
**Date:** 2026-04-15  
**Component:** `src/static/phone_relay.html` + `src/chat_server.py` (/phone endpoint)

## Overview

Full PWA implementation for Ethos Kernel field tests (F0–F3). The phone client collects real-world sensor data and streams it to the kernel via WebSocket.

**Key Features:**
- ✅ Battery status (Battery API)
- ✅ Accelerometer jerk (DeviceMotion Event)
- ✅ Microphone level (AudioWorklet with ScriptProcessorNode fallback)
- ✅ Silence detection
- ✅ WebSocket streaming (2 Hz default, configurable)
- ✅ Session pairing with token
- ✅ Pause/resume/end controls
- ✅ Real-time kernel action readback
- ✅ Trusted place toggle
- ✅ Sensor visualization bars

## File Structure

```
src/
  static/
    phone_relay.html           (17.6 KB, single-file PWA)
  chat_server.py              (modified @app.get("/phone") endpoint)
```

## Implementation Details

### 1. Sensor APIs

#### Battery Status
- **API:** Battery Status API (deprecated but widely available)
- **Fallback:** Silent degradation (null value)
- **Data:** Percentage (0–100)
- **Update:** Event-driven (battery.levelchange)

#### Accelerometer Jerk
- **API:** DeviceMotionEvent
- **Calculation:** √(x² + y² + z²) in m/s³
- **Normalization:** Clamped to [0, 1] at 20 m/s³
- **Update:** High frequency (≥10 Hz device-native)

#### Microphone Level
- **API:** AudioWorklet (Web Audio API)
- **Fallback:** ScriptProcessorNode (deprecated but universal)
- **Calculation:** RMS energy → dB (20 log₁₀(rms + 1e-6))
- **Silence Detection:** Level < -40 dB
- **Update:** Periodic (tied to audio frame size, ~20 ms)

### 2. WebSocket Integration

**Path:** `/ws/chat` (existing kernel chat endpoint)

**Frame Format:**
```json
{
  "role": "sensor_relay",
  "text": "[Field session: <session_id>]",
  "sensor": {
    "battery": 87,
    "jerk": 2.5,
    "noise": -15.3,
    "silence": 0,
    "trusted_place": false
  }
}
```

**Rate Limiting:** Token bucket (default 2 Hz / 500 ms)
- Configurable via `KERNEL_FIELD_SENSOR_HZ` env var
- Prevents misbehaving phones from saturating kernel thread pool

### 3. Session Lifecycle

```
[User taps "Start Session"]
  ↓
[Prompt for pairing token]
  ↓
POST /control/pair {"token": "..."}
  ↓
[Server validates token, returns field_session_id]
  ↓
localStorage.setItem('field_session_id', ...)
  ↓
[WebSocket connects to /ws/chat with sensor: role="sensor_relay"]
  ↓
[Periodic WebSocket frames sent at 2 Hz]
  ↓
[User taps "Pause" / "Resume" / "End"]
  ↓
POST /control/session {"action": "pause|resume|end"}
  ↓
[On "end": POST /control/session {"action": "end"}]
  ↓
[Server flushes session manifest to experiments/out/field/<session_id>/manifest.json]
  ↓
localStorage.removeItem('field_session_id')
  ↓
[PWA resets to idle state]
```

### 4. UI Components

**Buttons (Primary Control):**
- **Start Session:** Prompt for pairing token, initiate recording
- **Pause:** Stop sensor streaming (pause button becomes disabled)
- **Resume:** Resume streaming (start button becomes disabled again)
- **End:** Terminate session and flush manifest
- **Trusted Place:** Toggle to mark location as low-risk (boolean flag)

**Status Panel (Real-Time):**
- Current session status (Idle, Paired, Recording, Paused, Error)
- Session ID (first 8 chars + "...")
- Frames sent count
- Last action (echoed from kernel response)

**Sensor Visualization Panel (when recording):**
- Battery: percentage bar + value
- Jerk: acceleration bar + value (m/s³)
- Noise: dB level bar + value
- Silence: yes/no toggle bar + value

**Message Panel (Transient):**
- Success/error/info messages (auto-hide after 3 seconds for non-errors)

### 5. Security Constraints (Lab Scope)

✅ **Implemented:**
- LAN-only by default (KERNEL_FIELD_ALLOW_WAN=0)
- Pairing token printed once to stdout (never logged)
- Credentials 1-hour TTL
- No raw audio/video persisted (scalar summaries only)
- Session rate limiting (2 Hz default)
- Graceful fallbacks for unavailable APIs

⚠️ **Notes:**
- HTTPS not required for F0–F3 (LAN only)
- DeviceMotion/microphone may require `localhost` or self-signed HTTPS on some browsers
- Production deployment must add TLS before exposing beyond trusted LAN

### 6. Responsive Design

- **Max-width:** 480px (optimized for mobile)
- **Layout:** Single-column with gradient background
- **Colors:** Dark mode (1a1a1a base), accent gradients (cyan/red/orange/blue)
- **Typography:** System font stack (-apple-system, Segoe UI, Roboto, sans-serif)
- **Animations:** Smooth transitions (0.3s), hover effects with box-shadow
- **Accessibility:** Large touch targets (1rem padding), semantic HTML, color contrast

## Browser Compatibility

| Feature | iOS Safari | Android Chrome | Notes |
|---------|-----------|---|---|
| Battery API | ⚠️ Partial | ⚠️ Partial | Deprecated; may not work |
| DeviceMotion | ✅ iOS 15+ | ✅ Chrome 95+ | Requires HTTPS or localhost |
| AudioWorklet | ⚠️ iOS 14.7+ | ✅ Chrome 76+ | Falls back to ScriptProcessorNode |
| WebSocket | ✅ iOS 5+ | ✅ Chrome 16+ | Native support |
| localStorage | ✅ iOS 5+ | ✅ Chrome 4+ | For session persistence |
| PWA (installable) | ✅ iOS 15.4+ | ✅ Chrome 39+ | Via Web App Manifest (future) |

## Testing

### Unit Tests
- Path: `tests/test_field_control.py` (pending)
- Coverage:
  - Pairing token validation
  - Session state transitions
  - Rate limiter (token bucket)
  - WebSocket frame format validation
  - Manifest flush on session end

### Integration Tests
- Field test protocol validation (PROPOSAL_FIELD_TEST_PLAN.md)
- Real sensor data ingestion
- Decision-core invariance under sensor input
- Audit trail recording

### Manual Testing (F0 Pilot)
1. Enable `KERNEL_FIELD_CONTROL=1`
2. Set `KERNEL_FIELD_PAIRING_TOKEN=test_token_12345`
3. Open `/phone` endpoint on mobile device
4. Tap "Start Session", enter pairing token
5. Verify:
   - Battery bar updates (if available)
   - Jerk bar responds to device motion
   - Noise bar responds to sounds
   - WebSocket frames appear in server logs
   - Final_action echoed back to UI
6. Tap "Pause", verify frames stop
7. Tap "Resume", verify frames resume
8. Tap "End", verify session manifest written to `experiments/out/field/<session_id>/manifest.json`

## Deployment

### Minimal Setup
```bash
export KERNEL_FIELD_CONTROL=1
export KERNEL_FIELD_PAIRING_TOKEN=$(openssl rand -hex 16)
python src/chat_server.py
# Token printed to stdout
# Open http://127.0.0.1:8765/phone
```

### Production Setup (Future)
- [ ] Add `src/static/manifest.json` (PWA manifest for installability)
- [ ] Enable HTTPS (self-signed cert for LANor production cert)
- [ ] Add service worker for offline resilience
- [ ] Configure environment variables in `.env`

## Known Limitations

1. **Battery API Deprecation:** Browser vendors phasing out Battery Status API. Phone may report null level. UI gracefully handles this.
2. **Audio Permission Flow:** iOS requires explicit user permission; may block on some configurations.
3. **DeviceMotion Sensor Drift:** Raw accelerometer data includes gravity (9.8 m/s²) and bias. Kernel should normalize or use calibration.
4. **No Calibration UI:** Phone doesn't provide per-session sensor calibration. Future: add zero-point button for jerk.
5. **Single Phone per Session:** Current design assumes one phone per kernel instance. Multi-phone relay requires architecture change (router, per-phone rate limiters).

## References

- [ADR 0017](./adr/0017-smartphone-sensor-relay-bridge.md) — Architecture decision record
- [PROPOSAL_FIELD_TEST_PLAN.md](./proposals/PROPOSAL_FIELD_TEST_PLAN.md) — F0–F3 field test protocol
- [SENSOR_CONTRACTS.md](./docs/SENSOR_CONTRACTS.md) — SensorSnapshot schema (if exists)
- Web APIs:
  - [Battery Status API](https://developer.mozilla.org/en-US/docs/Web/API/Battery_Status_API)
  - [DeviceMotionEvent](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent)
  - [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
  - [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

**Status:** ADR 0017 implementation complete ✅  
**Next Steps:**
1. Test on real devices (F0 pilot)
2. Collect sensor calibration data
3. Add PWA manifest + service worker (v0.1.1)
4. Production TLS + secret store (before external deployment)

**Owner:** master-claude team  
**Last Updated:** 2026-04-15
