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

## Security gate

Run `pytest tests/core/ -q` before committing. All tests must pass.

## Disclaimer

Any reference to third-party trademarks is purely for descriptive purposes and does not imply affiliation or endorsement.
