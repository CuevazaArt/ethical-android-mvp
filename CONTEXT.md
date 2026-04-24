# Session Context (auto-updated after each block)

> Read THIS file first. Only read AGENTS.md or CONTRIBUTING.md if you need clarification on rules.

## Current state

- **Version:** V1.0 (Post-Phase 15 Consolidation)
- **Architecture:** Async Tri-Lobe (Perceptive, Limbic, Executive) + CorpusCallosum event bus
- **LLM:** Ollama local (llama3.2:1b). Zero cloud API dependency for chat.
- **Last merge to main:** 2026-04-23

## Open tasks

<!-- Move tasks here from PLAN_WORK_DISTRIBUTION_TREE.md when they become active -->
_No pending blocks. Open a new block or run adversarial audit._

## Key files for current work

| Area | Files |
|------|-------|
| Kernel entry | `src/kernel.py` |
| Lobes | `src/kernel_lobes/*.py` |
| Modules | `src/modules/{ethics,cognition,memory,social,governance,somatic,perception,safety}/` |
| Tests | `tests/` (run: `pytest tests/ -q`) |
| Security gate | `python scripts/eval/adversarial_suite.py` |
| Sync tool | `python scripts/swarm_sync.py --block <ID> --msg "<desc>"` |

## Recent changes (last 3 blocks)

- **Block 40.6:** Fixed LLM stream format for Nomad PWA (raw prose instead of JSON)
- **Block 40.5:** Fixed LLM_MODE being ignored; embedding model fallback
- **Block 40.4:** Fixed plain-text Ollama response handling
