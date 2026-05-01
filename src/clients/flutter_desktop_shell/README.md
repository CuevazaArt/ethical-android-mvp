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

## Voice state binding (50.4C)

The desktop UI now reads backend voice state from `/api/status`:

- `voice_turn_state` (`mic_off`, `listening`, `transcribing`, `responding`)
- `voice_turn_state_at` (epoch timestamp)

When the backend exposes these fields, the Voice panel switches from fallback mode
to server-bound mode automatically.

## Windows packaging baseline (50.5B)

From repository root:

```powershell
pwsh -File scripts/build_windows_desktop_release.ps1
```

Common options:

```powershell
pwsh -File scripts/build_windows_desktop_release.ps1 -SkipClean
pwsh -File scripts/build_windows_desktop_release.ps1 -OutDir dist/desktop/windows
```

The script writes release artifacts and `ARTIFACTS.txt` manifest into the output directory.

### Rollback procedure (release ops)

1. Stop the running desktop shell process.
2. Keep a backup of the current release directory.
3. Restore the last known-good artifact package.
4. Start `flutter_desktop_shell.exe` and verify kernel connectivity (`/api/ping`, `/api/status`).
5. If verification fails, revert to the previous backup and register incident notes.

When a release is built with `scripts/build_windows_desktop_release.ps1`, a
`ROLLBACK_CHECKLIST.txt` file is emitted alongside artifacts.

## Voice UX demo (Block 50.4A)

- The app now includes a dark voice panel named `Voice loop surface`.
- Current behavior:
  - Uses server state if `voice_state` / `voice_turn_state` fields appear in health payload.
  - Falls back to `mic off` if `stt_available` is false.

## Re-entry gates panel (Block 52.4)

- The desktop shell now includes a dedicated `Re-entry readiness gates` card.
- Gates `G1..G5` are rendered as status badges (`PASS`, `IN PROGRESS`, `FAIL`, `UNKNOWN`).
- If `/api/status` exposes `reentry_gates`, the panel switches to server source mode.
- If `reentry_gates` is missing, the panel stays in fallback mode and labels this explicitly.
- Backend support was added in block 52.5 (`src/server/app.py` -> `/api/status.reentry_gates`).

## Windows Packaging Baseline (Block 50.5A)

Windows-first reproducible release flow is now standardized through:

- Script: `scripts/build_windows_desktop_release.ps1`
- App module: `src/clients/flutter_desktop_shell`
- Output baseline: `dist/desktop/windows`

### Reproducible build (release)

From repository root (PowerShell):

```powershell
.\scripts\build_windows_desktop_release.ps1
```

Optional flags:

```powershell
.\scripts\build_windows_desktop_release.ps1 -SkipClean
.\scripts\build_windows_desktop_release.ps1 -OutDir "dist/desktop/windows_candidate"
```

What the script does:

1. Verifies `flutter` exists in `PATH`.
2. Runs `flutter --version`.
3. Runs app prep and validation:
   - `flutter clean` (unless `-SkipClean`)
   - `flutter pub get`
   - `flutter test`
   - `flutter build windows --release`
4. Copies runner release payload into `dist/desktop/windows`.
5. Writes `ARTIFACTS.txt` with expected files and launch hint.

### Expected artifacts registry

After a successful build, expect these artifacts under `dist/desktop/windows`:

- `flutter_desktop_shell.exe`
- `data/` directory (Flutter assets, `icudtl.dat`, runtime assets)
- `flutter_windows.dll`
- Runtime DLLs (`vcruntime*.dll`, `msvcp*.dll`) depending on machine/runtime
- `ARTIFACTS.txt` (generated build manifest)

### Smoke checklist (install / run / update)

Manual operator checklist for Windows baseline validation:

1. **Install baseline**
   - Copy `dist/desktop/windows` to a clean machine folder, for example `C:\EthosDesktop`.
2. **Run baseline**
   - Launch backend:
     - `uvicorn src.server.app:app --host 127.0.0.1 --port 8000`
   - Launch app:
     - `C:\EthosDesktop\flutter_desktop_shell.exe`
3. **Startup smoke**
   - Verify app opens without crash.
   - Verify status eventually reaches `Connected`.
   - Verify payload panel renders `/api/status` JSON.
4. **Transport resilience smoke**
   - Stop backend temporarily.
   - Verify UI state moves to retry behavior (`Retrying` / `Offline`) without app crash.
   - Restart backend and verify auto-recovery to `Connected`.
5. **Manual update smoke**
   - Build a new release with the script.
   - Replace old app folder with new `dist/desktop/windows` payload.
   - Relaunch app and repeat startup smoke to confirm update viability.

### Operational notes

- This baseline is intentionally manual-first (no installer/updater automation yet).
- Keep `KERNEL_BASE_URL` defaulted to `http://127.0.0.1:8000` unless operator topology requires override.
- Do not alter backend contracts during packaging iterations.

## Dark Theme QA + Accessibility Checklist (Block 50.1C)

- Contrast pass for dark cards, badges, and status text in `Connected`, `Retrying`, and `Offline`.
- Connection badges expose semantic labels (`Connection status ...`) for assistive technologies.
- Health payload panel is marked as a readable/scrollable semantic region with visible focus border.
- Voice action buttons include tooltip hints and visible keyboard focus state.
- Widget tests cover dark-shell baseline and key voice-state transitions.
