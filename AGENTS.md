# Agent and Contributor Orientation — Ethos 2.0

This file is the entry point for humans and AI assistants working in this repository.

## Read first

- **[`CONTEXT.md`](CONTEXT.md) — START HERE.** Current state, open blocks, key files. (~30 lines.)
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — language policy, process, lint.
- V1 architectural reference: `git checkout v15-archive-full-vision` (frozen, do NOT modify).

## Authority

1. **Juan (L0):** Absolute authority. Only person who can merge to `main`.
2. **Project rules:** This file defines the normative framework.
3. **AI agents (Men Scouts):** Autonomous executors assigned to vertical blocks. One agent per block. Full responsibility.

## Men Scout Code — The 7 Laws

1. **Deliver Features, Not Code.** A block is not "I wrote 500 lines". A block is "the chat responds in terminal, here is the log".
2. **Own Your Block.** One agent = one block = complete responsibility. No handoffs mid-block.
3. **Prove or It Doesn't Exist.** Every block closes with evidence: execution log, passing test, or screenshot. Without demo, the block is reverted.
4. **Vertical Integration.** Each block includes: implementation + test + CONTEXT.md update. No isolated "docs-only" or "refactor-only" blocks.
5. **Minimal Surface Area.** If it can be done in 50 lines, don't write 500. A new file requires justification: why doesn't it fit in an existing one?
6. **Prune Without Mercy.** If something becomes obsolete, delete it in the same block. Don't comment out. Don't archive. Git preserves history.
7. **Single Source of Truth.** One concept = one file. No duplicates, no alternatives, no "v2" coexisting with "v1".

## Boy Scout Rules (inherited, always active)

1. **Harden-In-Place:** Fill empty `try/except` blocks, add type hints, sanitize inputs.
2. **Anti-NaN:** If you touch math or latency logic, ensure results cannot be `NaN` or `Inf`. Use `math.isfinite()`.
3. **Latency metrics:** New loops or sensory paths must log latency with `time.perf_counter()`.
4. **Zero dead code:** If you find obsolete code — delete it now.

## LLM Quality Rules (for advanced agents)

1. **Full Context:** Before touching a file, read the entire file. Don't assume "the rest is fine".
2. **One Correct Pass:** Make the right change the first time. Think before writing.
3. **Test First:** For bugs: reproduce with a test BEFORE writing the fix. For features: define "works" BEFORE implementing.
4. **Architectural Coherence:** Before creating a new module, ask: does something already do this? If yes, extend it.

## Block Assignment Format

Each Men Scout receives:
- Block number (e.g., V2.5)
- Concrete deliverable (e.g., "WebSocket chat functional on localhost:8000")
- Files they may touch
- Demo they must produce
- Files they must read first
- **Recommended LLM models** (ranked, see below)

## LLM Model Recommendation (L1 → L0) & Token Economy V3

**Nueva Directiva Estratégica (2026-04-26):** Operamos bajo un protocolo extremo de ahorro de tokens y cuota. El **90% del trabajo** (implementación, tests, refactoring) debe asignarse por defecto a **Gemini 3 Flash**.
Los modelos Premium (ej. Gemini 3.1 Pro High) quedan **suspendidos temporalmente** del roster.
Los modelos "Thinking" (Opus/Sonnet) o "Pro Low" se reservan estrictamente para diseño arquitectónico abstracto o conflictos de integración intratables.

**Identidad y Responsabilidad del Scout:**
- **Identidad Implícita:** Los agentes no se registran. Se identifican por su bloque (ej. "Scout-V2.80").
- **Responsabilidad Absoluta:** Un Men Scout **NUNCA es relevado de su guardia** hasta que entregue código integrado, testeado y funcional. No se aceptan entregas a medias ni "pasar el problema" a otro modelo.

**Rol de L1 (The Watchtower):**
- L1 (yo) debe atender a los scouts y realizar **micro-merges constantes** al repositorio. La latencia entre miembros del enjambre es el enemigo; si no hacemos commit continuo de cada victoria discreta, el estado se pierde y el enjambre alucina.

| Task type | Needs | Default Assignment |
|-----------|-------|--------------------|
| Arquitectura, Conflictos Severos | Razonamiento profundo | Claude Sonnet 4.6 (Thinking) / Gemini 3.1 Pro (Low) |
| Implementación de features | Velocidad, bajo costo | Gemini 3 Flash |
| Corrección de bugs, Unit Tests | Velocidad, bajo costo | Gemini 3 Flash |
| Refactorización mecánica | Velocidad, bajo costo | Gemini 3 Flash |

**Formato del Prompt (L1 genera para que L0 copie y pegue al Scout):**
```markdown
[IDENTIDAD]: Scout-[V2.X]
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — *Solo usar si Flash falla 3 veces seguidas.*
```

## Block Closure Format

```
## Block V2.X — [Name]
- **Status:** CLOSED ✅
- **Files created/modified:** [list]
- **Files deleted:** [list, if any]
- **Demo:** [execution log or test reference]
- **Tests:** `pytest tests/core/test_X.py` — X passed, 0 failed
```

## Prohibitions

- ❌ Do NOT create a new file without written justification
- ❌ Do NOT open a block that depends on an unclosed block
- ❌ Do NOT harden code that has no demo
- ❌ Do NOT create policies, fallbacks, or degradation paths for code that doesn't work yet
- ❌ Do NOT touch files outside the assigned block scope
- ❌ Do NOT push to `main` directly (L0-only)

## Token Economy Rules

- **No greetings, no sign-offs.** Start with the work, end with the result.
- **No project history.** Agents don't need to know about V1 or past decisions.
- **Exact file paths, not "explore".** Every task specifies exactly which files to read and modify.
- **Change limits per block.** Each block has a max line-change budget. Don't rewrite files.
- **Log, not essay.** Block closure is: files touched, test command, demo log. Not 3 paragraphs.
- **Error = immediate fix.** Don't document the error and propose a plan. Just fix it.
- **If stuck, implement the simplest solution that passes the test. Don't optimize.**
## L0 Operations Protocol

### Short commands (L0 → L1)

L0 uses minimal commands. L1 interprets and acts.

| L0 says | L1 does |
|---------|---------|
| `siguiente` | Reads CONTEXT.md, generates next block prompt with `[MODELOS]` |
| `asignar enjambre: [X] Flash, [Y] Sonnet...` | L0 allocates compute budget. L1 partitions the next milestone into exact tasks to fit this budget, generating parallel prompts. |
| `dame prompt V2.X` | Generates prompt for specific block |
| `review` | Audits last Men Scout output: checks demo, tests, file scope |
| `merge` | Runs pre-commit checks, commits, syncs with origin/main |
| `estado` | Reports: current block, open blocks, test status, repo health |
| `conflicto en [file]` | Reads file, resolves conflict, explains what was kept/dropped |
| `poda` | Identifies unused files in src/, proposes deletions |
| `el agente falló en X` | Generates correction prompt for same block |
| `se cortó en V2.X` | Evaluates partial work, generates continuation prompt (see below) |
| `cambio de oficina` | Generates context handoff summary (see below) |
| `roster: +Model-X, -Model-Y` | Updates model roster in AGENTS.md |

### Agent interruption recovery ("se cortó")

When an agent's quota runs out or execution stops mid-block:

1. L0 says `se cortó en V2.X` to L1.
2. L1 checks ground truth: `git status`, `git diff`, `python -m src.core.status`, `pytest tests/core/ -q`.
3. L1 assesses:
   - **What was done?** Files created/modified, tests added.
   - **What still works?** Do existing tests still pass?
   - **What remains?** Comparing against the original prompt deliverables.
4. L1 generates a **continuation prompt** for a new agent session. This prompt:
   - Starts with `[CONTINUACIÓN]` not `[BLOQUE]` so the agent knows it's picking up mid-work.
   - Lists exactly what's already done (so the agent doesn't redo it).
   - Lists only the remaining deliverables.
   - Includes the same `[SI TE TRABAS]` and `[REGLAS]` as the original.
5. If the partial work broke tests → L1 generates a fix prompt instead.
6. If the partial work is complete but uncommitted → L0 says `merge` directly.

### Context transfer between IDEs ("cambio de oficina")

When L0 moves from one environment to another (e.g., Antigravity → Cursor → terminal):

1. L0 says `cambio de oficina` in the current IDE.
2. L1 generates a **handoff block**: a compact summary of current state, active block, last changes, and pending work. Designed to be pasted as first message in the new environment.
3. In the new environment, L0 pastes the handoff block. The new L1 instance reads it and continues.

**CONTEXT.md is the persistent bridge.** Any L1 in any IDE reads CONTEXT.md first and is immediately oriented. The handoff block adds ephemeral details (mid-block progress, uncommitted changes).

### Reviewing Men Scout work

When a Men Scout finishes a block, L0 reviews by saying `review`. L1 checks:

1. **Demo exists?** — Did the agent produce an execution log, test output, or screenshot?
2. **Tests pass?** — `pytest tests/core/ -q` runs clean?
3. **Scope respected?** — Did the agent only touch files listed in the prompt?
4. **Line budget respected?** — Did the agent stay within the max change limit?
5. **CONTEXT.md updated?** — Is the block marked as CLOSED with correct info?

If all 5 pass → L0 says `merge`. If any fail → L0 says `el agente falló en X`.

### Orchestrating a Swarm Cycle (Proactive Allocation)

Instead of moving block by block, L0 can provision a "Compute Budget" for a cycle.
1. **L0 says:** `asignar enjambre: 10 Flash, 2 Sonnet, 1 Opus`.
2. **L1 designs the plan:** L1 analyzes the next major architectural milestone (e.g., "Parasite Mesh") and partitions the work.
   - The 1 Opus prompt will be pure architecture (e.g., JSON schema definitions).
   - The 2 Sonnet prompts will be complex implementations (e.g., Audio processing).
   - The 10 Flash prompts will be mechanical (e.g., parsing, unit tests, logging, formatting).
3. **L0 deploys:** L0 copy-pastes the generated prompts to the respective models in parallel.
4. **L1 acts as Watchtower:** As L0 brings back the results, L1 constantly merges (micro-commits) to keep the state clean.
5. **Conflict Resolution:** If an agent fails or causes a merge conflict, L1 generates a strict correction prompt. L0 prioritizes re-deploying this specific agent before continuing with the rest.

### Merge and sync flow

When L0 says `merge`:
1. L1 runs `pytest tests/core/ -q` (must pass).
2. L1 runs `python scripts/pre_commit_check.py` if available (lint/format).
3. L1 commits with standardized message: `"V2.X: [Block name] — [one-line summary]"`.
4. L1 runs `git pull origin main --rebase` to sync.
5. If conflicts → L1 resolves and explains. L0 approves final state.
6. L0 pushes when ready: `git push origin main`.

### Conflict resolution

Conflicts are resolved by L1 with these priorities:
1. **New code wins over old code** (V2 over V1).
2. **Working code wins over scaffold** (tested over untested).
3. **Smaller change wins** when both sides are equivalent.
4. L1 always explains what was kept and what was dropped. L0 approves.

## Security gate

Run `pytest tests/core/ -q` before committing. All tests must pass.

## Disclaimer

Any reference to third-party trademarks is purely for descriptive purposes and does not imply affiliation or endorsement.
