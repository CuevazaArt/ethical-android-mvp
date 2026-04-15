# Phased plan: runtime → persistence → local LLM

Goal: move from research to a **live process** without letting any layer **override kernel ethics**. The decision core remains `EthicalKernel` (MalAbs, Bayes, poles, will); everything else is perception, tone, state, and storage.

---

## Non-negotiable principles

1. **No background loop** chooses actions or injects `CandidateAction` instances that have not passed through `process` / `process_chat_turn`. Drives and monologue **do not** replace the kernel.
2. The **LLM** (local or API) **does not** set policy; it only translates signals ↔ text and style (as in theory docs).
3. Any “interrupt” or user alert is a **UX layer** (notification), not a second veto parallel to MalAbs.
4. **Augenesis** stays **optional** and off the default path ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

---

## Phase 1 — Execution runtime (priority)

**Goal:** a process that **stays alive**, handles I/O (chat/WebSocket), and can schedule auxiliary work **without blocking** conversation, without changing ethical semantics.

| Sub-phase | Work | Ethical limits |
|-----------|------|----------------|
| **1.1 Contract** | Document in code/docs which async tasks are allowed: e.g. timers for `execute_sleep`, health, metrics. | Forbidden: tasks that call “decision” APIs outside `process` / `process_chat_turn`. |
| **1.2 Current baseline** | `python -m src.runtime` and `python -m src.chat_server` serve the same ASGI (`get_uvicorn_bind` / `run_chat_server`). See [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). | No duplicated ethical logic outside the kernel. |
| **1.3 Async orchestration** | A thin module (e.g. `src/runtime/`) that: (a) starts the ASGI server; (b) optionally registers **one** background “maintenance” task (e.g. reminder to run `execute_sleep` on a simulated schedule or explicit event). | Background **must not** generate user-facing responses or change ethical weights; at most enqueue an event the **same** chat flow could consume (later phase). |
| **1.4 Monologue / drives in background** | **Telemetry only**: logs or internal queue of “impulses” from `DriveArbiter.evaluate(kernel)` as already implemented, without mandatory LLM in the loop. | If LLM is later used for private monologue text, that is Phase 3 and remains text-only, not action. |

**Phase 1 deliverable:** documented process + clear entrypoint + tests that the kernel is not invoked from undocumented sites (optional: static test or convention).

**Suggested order:** 1.2 → 1.1 → 1.3 → 1.4.

**Repo status (Phase 1.3–1.4):** if `KERNEL_ADVISORY_INTERVAL_S` is a positive number, each `/ws/chat` connection starts `advisory_loop` in the background and stops it when the session closes (`src/chat_server.py`, `src/runtime/telemetry.py`). No decisions or LLM; only periodic `DriveArbiter.evaluate`.

---

## Phase 2 — Persistence and database

**Goal:** identity and episodes **survive** restart, with a versioned schema.

| Sub-phase | Work | Notes |
|-----------|------|-------|
| **2.1 Port** | DTO `KernelSnapshotV1` + `extract_snapshot` / `apply_snapshot` in `src/persistence/kernel_io.py`. | Covers episodes, identity, forgiveness, weakness, Bayes/locus/variability, DAO audit, `pruned_actions`. |
| **2.2 JSON adapter** | `JsonFilePersistence` (`src/persistence/json_store.py`). | Tests: `tests/test_persistence.py` (in-memory roundtrip, file, double serialization). |
| **2.2b SQLite (optional)** | Same DTO, another `blob` JSON column. | `SqlitePersistence` in `src/persistence/sqlite_store.py` (`kernel_snapshot` table, row `id=1`). |
| **2.3 Encryption (implemented for JSON checkpoints; SQLite pending)** | For deployments with sensitive on-disk data, JSON checkpoint persistence supports optional Fernet encryption via `KERNEL_CHECKPOINT_FERNET_KEY` (keys must stay outside the repo). SQLite-at-rest encryption remains an external/deployment concern unless a dedicated encrypted adapter is introduced later. | Implemented in `src/persistence/json_store.py` for JSON checkpoint payloads. This is confidentiality-only and does not replace OS permissions or access control. |
| **2.4 Runtime integration** | WebSocket (`src/chat_server.py`): `try_load_checkpoint` on connect; `on_websocket_session_end` on disconnect; `maybe_autosave_episodes` after each turn. Env: `KERNEL_CHECKPOINT_*` (see `src/persistence/checkpoint.py`). | Concurrency: a shared file across many connections can race. |

**Dependency:** Phase 1 stable (at least entrypoint and process lifecycle).

---

## Phase 3 — Local LLM (e.g. Ollama)

**Goal:** local perception and voice for privacy, without changing **who** decides.

| Sub-phase | Work | Limits |
|-----------|------|--------|
| **3.1 LLM contract** | Clear interface vs `LLMModule`: `complete(system, prompt, …)` async or sync per call site. | Same boundary as today: kernel only calls perceive/communicate/narrate. |
| **3.2 Ollama adapter** | `LLMModule` with `LLM_MODE=ollama`: `POST /api/chat` via `httpx` (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`). | If the model returns invalid JSON, fall back only where existing fallback already applies; perceive/communicate/narrate prompts expect JSON. |
| **3.3 Configuration** | Env vars: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `USE_LOCAL_LLM=true`. | Document in README. |
| **3.4 LLM monologue (optional)** | Only after 3.2: generate internal monologue text for logs/UI, **never** as direct input to MalAbs. | Review prompts so they do not “instruct” the kernel. |

**Repo status (Phase 3):** `src/modules/llm_backends.py` — **`OllamaCompletion`** is the primary open-source path (`LLM_MODE=ollama`, `OLLAMA_*`); `LLMModule` selects the backend via `resolve_llm_mode` / `LLM_MODE` / `USE_LOCAL_LLM`; optional monologue via `KERNEL_LLM_MONOLOGUE` in `optional_monologue_embellishment` (chat). README documents `OLLAMA_*`, default model `llama3.2:3b`, tests in `tests/test_ollama_llm.py`, `tests/test_llm_phase3.py`. (Additional pluggable backends may exist in code for development; operators should follow Ollama in docs.)

**Dependency:** Phase 1 helps avoid blocking the event loop; Phase 2 is independent (persistence can ship before or after local LLM depending on privacy vs data priority).

---

## Global recommended order

1. **Phase 1** (runtime + contract + entrypoint + safe background tasks).  
2. **Phase 2** (persistence: port → SQLite/JSON → startup/shutdown integration).  
3. **Phase 3** (Ollama or another local backend behind the LLM port).

Between phases: update [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md), [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md), and the README with “what is implemented”.

---

## Do not do until foundations exist

- Replace `process` with an “autonomous” LLM agent.
- Mix augenesis into the default path without opt-in.
- Background loops that invoke the LLM without frequency limits and without tests.

---

## References in this repo

- Runtime and state: [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md)  
- Theory and v6+ layers: [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)  
- Current chat server: `src/chat_server.py`, `src/kernel.py`
