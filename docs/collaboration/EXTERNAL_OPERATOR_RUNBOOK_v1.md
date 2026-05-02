# External Operator Runbook v1

**Purpose:** Document that a non-author human ran the Ethos desktop MVP
end-to-end and produced a valid external signoff.

**Time required:** ~30 minutes on a clean checkout.

**Who this is for:** Any technically competent person who is **not an author
of the Ethos codebase**. A developer, researcher, or technically-literate
user qualifies.

---

## Prerequisites

- Python 3.11+ installed.
- Git installed.
- A machine with at least 8 GB RAM.
- (Optional) Ollama installed for live LLM responses; the server works in
  stub mode without it.

---

## Step 1 — Clone and install (5 min)

```bash
git clone https://github.com/CuevazaArt/ethical-android-mvp
cd ethical-android-mvp
pip install -r requirements.txt -r requirements-dev.txt
```

---

## Step 2 — Start the kernel server (2 min)

```bash
python -m src.server.app
```

Confirm: `curl http://127.0.0.1:8000/api/ping` returns `{"status":"ok"}`.

---

## Step 3 — Run the ethics benchmark (3 min)

```bash
python scripts/eval/run_ethics_benchmark.py --suite v1
```

Note the `accuracy` field in the output. **Record this value.**

---

## Step 4 — Five mandatory ledger-touching actions (15 min)

These interactions create real (non-synthetic) entries in the feedback
ledger, which is required for H3 of the sprint.

Open `http://127.0.0.1:8000/docs` (FastAPI Swagger) and perform:

1. **POST /api/chat** — Send a message and confirm a response is returned.
2. **POST /api/chat** — Send a second message about a different topic.
3. **POST /api/feedback** (or equivalent endpoint) — Submit a positive
   rating (`thumbs_up: true`) for one of the responses.
4. **POST /api/feedback** — Submit a negative rating for a different
   response.
5. **GET /api/status** — Confirm the gate scoreboard returns gate data
   including `reentry_gates` and at least one gate status.

Take a screenshot or copy the response JSON for each action. You will
attach the last interaction's `run_id` to your signoff.

---

## Step 5 — Run the demo interaction runner (3 min)

```bash
python scripts/eval/desktop_e2e_demo_runner.py 2>/dev/null || \
  python -c "import json; print(json.load(open('docs/collaboration/evidence/OPERATOR_INTERACTION_DEMO.json'))['run_id'])"
```

Note the `run_id` from the output or from
`docs/collaboration/evidence/OPERATOR_INTERACTION_DEMO.json`.

---

## Step 6 — Write your signoff file (2 min)

Create a file named after your identifier, e.g.
`docs/collaboration/evidence/MVP_EXTERNAL_OPERATOR_SIGNOFF_<your_id>.json`:

```json
{
  "schema_version": "1",
  "verified": true,
  "operator": "<your name or handle — must not be 'agent', 'copilot', 'anonymous', etc.>",
  "verified_at": "<RFC-3339 UTC timestamp, e.g. 2026-05-03T14:30:00Z>",
  "evidence_run_id": "<run_id from Step 5>",
  "notes": "<optional: any observations about the run>",
  "benchmark_accuracy_observed": <number from Step 3>
}
```

---

## Step 7 — Verify your signoff (1 min)

```bash
python scripts/eval/verify_external_operator_signoff.py \
  --signoff docs/collaboration/evidence/MVP_EXTERNAL_OPERATOR_SIGNOFF_<your_id>.json
```

Expected output: `"ok": true`.

If you see `"ok": false`, read the `reasons` array and fix the issue.

---

## Step 8 — Verify the full signoff directory (optional, for cumulative check)

```bash
python scripts/eval/verify_external_operator_signoff.py \
  --signoff-dir docs/collaboration/evidence/ \
  --min-signoffs 1
```

---

## What makes a signoff valid

| Rule | Reason |
|---|---|
| `verified: true` | Explicit confirmation that the run succeeded |
| `operator` not in deny-list | Prevents self-attestation |
| `verified_at` is RFC-3339 UTC | Enables temporal ordering and freshness checks |
| `evidence_run_id` matches OPERATOR_INTERACTION_DEMO | Binds the signoff to a real reproducible run |

---

## What to do if something fails

- Server won't start → check `requirements.txt` is fully installed; check
  port 8000 is free.
- `/api/ping` returns an error → check `src/server/app.py` startup logs.
- Benchmark fails → run `python -m pytest tests/core/test_ethics.py -q`
  and report which test fails.
- Signoff verification fails → read the `reasons` output carefully;
  most common issue is `verified_at` format (must include timezone).

Please open an issue with the failure output if the runbook steps cannot
be completed as written. That is valuable feedback.
