# Session Context — Ethos

> Read this file first. Authoritative current state.

## Current product

- **Active surface:** Flutter Desktop MVP + Python/FastAPI kernel.
- **Business-logic authority:** `src/core/` only.
- **Server boundary:** `src/server/` consumed by Flutter Desktop.
- **Mobile Android:** freeze-lane (security/health maintenance only).

## Current measured numbers

- **Ethics benchmark:** 30/30 PASS, 0 HARD_FAIL on `evals/ethics/dilemmas_v1.json`
  (run `scripts/eval/run_ethics_benchmark.py --suite v1`).
- **Baseline of record:** `evals/ethics/BASELINE_v1.json` at 27/28
  (96.43%). The post-fix delta (+3.57 pp on +2 dilemmas) is documented
  in `docs/proposals/ETHICAL_BENCHMARK_BASELINE.md`. The baseline is
  preserved as the historical reference; it is **not** overwritten.
- **Tests:** 12/12 in `tests/core/test_ethics.py`. Full suite: see
  `python -m pytest tests/ -q`.

## Open debt (be honest about what is not done)

1. **No external operator signoff.** The MVP closure pipeline
   (`verify_external_operator_signoff.py`, `--signoff-dir`) reports
   `0 valid signoffs`. The README states "external signoff pending".
   Until a non-author runs the runbook
   (`docs/collaboration/EXTERNAL_OPERATOR_RUNBOOK_v1.md`) and produces a
   `verified=true` JSON, no `v1.0` or `v1.1-mvp-evaluable` tag should
   be cut.
2. **Curated benchmark only.** The 30/30 number is on dilemmas authored
   in this repository. There is **no measurement on an external dataset
   (e.g., ETHICS by Hendrycks et al., Moral Stories)** and therefore no
   evidence the evaluator generalizes. See `docs/CRITIQUE_SPRINT_V2_141_146.md`
   for the full reading.
3. **Audio capture pipeline:** `PENDING_HARDWARE`. Voice turn metrics
   are paper, not measured.

## Last execution wave

### V2.141–V2.146 — Ethics benchmark fix + governance cleanup

- C003 (footbridge trolley) moved from HARD_FAIL to PASS by adding a
  deontological-weight override in `EthicalEvaluator.score_action` when
  `action.force > 0.7`. Two new adversarial dilemmas (A009, A010) extend
  the benchmark to 30 dilemmas exercising the same instrumental-means
  pattern.
- Regression test: `test_cbr_does_not_anchor_high_force_protection_intervention`
  in `tests/core/test_ethics.py`.
- **Honest critique of this wave:** see `docs/CRITIQUE_SPRINT_V2_141_146.md`.
  The fix is a heuristic, not the architectural CBR improvement the
  original plan called for; the new dilemmas were authored after the
  failure mode was understood; the 100% number reflects overfitting
  to a curated suite.

### V2.147 — Cleanup (this commit)

- Removed swarm-era documents and vocabulary: `docs/changelogs_l2/*`,
  `docs/SWARM_*`, `docs/proposals/SWARM_P2P_THREAT_MODEL.md`,
  `docs/proposals/PROPOSAL_L1_*`, `docs/proposals/GLOSSARY_PROMPTS_AND_COMMANDS.md`,
  `docs/proposals/WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md`,
  `docs/ARCHITECTURE_NOMAD_V3.md`, `docs/VISION_NOMAD.md`. ~6,100 lines.
- Rewrote `AGENTS.md` (221 → ~80 lines): no Men Scouts, no L0/L1, no
  Watchtower, no `[BLOQUE]` prompt format. Kept only what maps to
  measurable engineering practice.
- Rewrote this `CONTEXT.md` (1003 → ~80 lines): kept current product
  state and last wave; dropped the historical pulse log (visible in
  git history).

## Next steps (concrete, not aspirational)

See `docs/CRITIQUE_SPRINT_V2_141_146.md § Way forward` for the full
reasoning. In short:

1. **External benchmark.** Wire the evaluator against a published
   ethics dataset and report the score honestly, even if low.
2. **A real external operator.** Either name the human, contact them,
   set a date — or remove the H3 requirement from the README. No
   "pending forever".
3. **Stop adding governance docs.** Code, tests, and measured numbers
   are the deliverables. The pulse log is in git.
