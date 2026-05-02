# MVP Operator Runbook (V2.122)

This runbook walks a non-author operator from a clean clone to a complete
desktop interaction with Ethos. It is the human-readable companion to
[`docs/collaboration/MVP_CHECKPOINT_RUNBOOK.md`](MVP_CHECKPOINT_RUNBOOK.md), and
its acceptance criteria are the Definition of Done for the V2.119–V2.128 model
development wave.

## Audience

You are a non-author operator with:

- A Windows or macOS workstation.
- Python 3.11+ installed.
- Flutter 3.41+ installed (`flutter --version` works).
- Optional: an Ollama backend reachable at `http://127.0.0.1:11434` for LLM
  responses. Without Ollama the kernel stays online but `/api/voice_turn`
  returns `LLM_UNAVAILABLE` and the chat reply path falls back to short stubs.

## What you will demonstrate

1. The kernel server starts and exposes `/api/ping`, `/api/status`,
   `/api/perception/audio`, and `/api/voice_turn`.
2. The Flutter desktop shell opens, connects to the kernel, and lets you hold
   a chat conversation over WebSocket.
3. The push-to-talk `Speak` button posts a `voice_turn` envelope and renders
   the reply with an explicit `latency: Xms` badge.
4. The diagnostics tab still surfaces transport health and the gate
   scoreboard.

## Step 1 — Clone and install Python deps

```bash
git clone https://github.com/CuevazaArt/ethos-kernel-antigravity.git
cd ethos-kernel-antigravity
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

## Step 2 — Run the kernel server

```bash
python -m src.server.app
```

Expected console output (truncated):

```
INFO     uvicorn.error:server.py:84 Started server process
INFO     uvicorn.error:on.py:48 Waiting for application startup.
INFO     uvicorn.error:on.py:62 Application startup complete.
INFO     uvicorn.error:server.py:216 Uvicorn running on http://127.0.0.1:8000
```

Verify in another terminal:

```bash
curl http://127.0.0.1:8000/api/ping
# {"pong":true,"uptime_s":N}
```

## Step 3 — Run the Flutter desktop shell

```bash
cd src/clients/flutter_desktop_shell
flutter pub get
flutter run -d windows   # or: flutter run -d macos
```

The window opens defaulting to the **Chat** tab. The chat status badge should
read `Chat connected` within ~2 seconds.

## Step 4 — Have a conversation

1. Type `hola, ¿quién eres?` in the chat input.
2. Press `Send`.
3. The Ethos bubble streams the reply, ending with chips for `action` and
   optional `ctx`.
4. Send at least two more turns to confirm the WebSocket handles continued
   exchange.

## Step 5 — Push-to-talk via voice_turn

1. Type any utterance, for example `dame un saludo corto`.
2. Press `Speak`.
3. The reply renders with chips that include `latency: Xms` and `action:
   voice_turn`. The status line below the title says `voice_turn ok (listen)`
   on success or `voice_turn error (NNN)` if the kernel rejects the request.

## Step 6 — Inspect diagnostics and gates

1. Switch to the **Diagnostics** tab.
2. Confirm:
   - `Connection states` card shows `Connected`.
   - `Re-entry readiness gates` shows G1, G2, G3, G4, G5 with the latest
     statuses (G2 may be `IN PROGRESS` until V2.127 closes it as
     `text_mediated`).
   - `Health payload` card displays the live `/api/status` JSON.

## Step 7 — Reproducible evidence (optional, for L1 review)

```bash
python scripts/eval/desktop_e2e_demo_runner.py \
  --output docs/collaboration/evidence/DESKTOP_E2E_DEMO_REPORT.json
```

Expected stdout (excerpt):

```
{
  "run_id": "desktop-e2e-demo-...",
  "passed": true,
  "steps": 5
}
```

The runner now exercises the `voice_turn` step in addition to ping, status,
audio, and post-turn status. The persisted JSON is the canonical G4 evidence
artifact.

## Troubleshooting

- **`Chat retrying`**: the server is not listening. Confirm step 2 succeeded
  and that nothing else occupies port 8000.
- **`voice_turn error (503)` with `LLM_UNAVAILABLE`**: start Ollama
  (`ollama serve`) or accept that voice_turn cannot complete on this host
  without an LLM backend. Chat still works because `/ws/chat` falls back to
  short canned messages when the LLM is offline.
- **Flutter window blank**: ensure `flutter doctor` is clean and that the
  `web_socket_channel` package was fetched by `flutter pub get`.

## Acceptance signal (Definition of Done)

If steps 1–6 succeed in order on a fresh clone, the V2.119–V2.121 wave is
demonstrably complete and the operator surface satisfies the README promise:
"Flutter Desktop MVP backed by the Python kernel server" with a real
interactive cycle and auditable trace chips on every reply.
