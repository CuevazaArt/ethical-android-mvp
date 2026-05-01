# Flutter Desktop Shell (Block 50.1)

Minimal desktop shell for Ethos Kernel with resilient transport:

- Heartbeat: `GET /api/ping` every 2 seconds.
- Health payload: `GET /api/status` on successful heartbeat.
- Reconnect policy: exponential backoff with short bounded delay (1s, 2s, 4s, 8s max).

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
