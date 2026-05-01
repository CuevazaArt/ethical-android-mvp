# Flutter Desktop Shell (Block 50.1)

Minimal desktop shell for Ethos Kernel with resilient transport:

- Heartbeat: `GET /api/ping` every 2 seconds.
- Health payload: `GET /api/status` on successful heartbeat.
- Reconnect policy: exponential backoff with short bounded delay (1s, 2s, 4s, 8s max).
- Voice UX surface (dark): machine-state panel for `mic_off -> listening -> transcribing -> responding`.

## Run

From this directory:

```bash
flutter pub get
flutter run -d windows
```

Optional kernel URL override:

```bash
flutter run -d windows --dart-define=KERNEL_BASE_URL=http://127.0.0.1:8000
```

## Local demo script

1. Start backend:
   - `uvicorn src.server.app:app --host 127.0.0.1 --port 8000`
2. Start desktop shell:
   - `flutter run -d windows`
3. Verify startup log:
   - `startup -> probing kernel`
   - `connected -> health payload received`
4. Stop backend for a few seconds and restart it:
   - App shows `retrying` and reconnects automatically without crash.

## Voice UX demo (Block 50.4A)

- The app now includes a dark voice panel named `Voice loop surface`.
- Current behavior:
  - Uses server state if `voice_state` / `voice_turn_state` fields appear in health payload.
  - Falls back to `mic off` if `stt_available` is false.
  - Supports explicit placeholder transitions with the `Next state` button.
- Demo log pattern:
  - `voice_ui -> listening (placeholder)`
  - `voice_ui -> transcribing (placeholder)`
  - `voice_ui -> responding (placeholder)`
