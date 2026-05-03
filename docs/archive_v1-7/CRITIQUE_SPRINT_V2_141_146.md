# Critique — Sprint V2.141–V2.146

> Honest reading of what the V2.141–V2.146 sprint delivered, what it
> claimed to deliver, and what would actually move the project forward.

## What the sprint claimed

From the original plan:

> Convertir el evaluador de "96.43% con un fallo estructural conocido"
> en "100% sobre baseline v1 con un fallo arreglado por mejora
> arquitectónica auditable", cerrar el último hito abierto del sprint
> anterior (H3), y dejar la gobernanza de modelos coherente con la
> práctica real.

Five hitos: H6 (C003 fixed), H7 (root cause architectural), H8 (H3
closed or honestly reassigned), H9 (`AGENTS.md` matches practice),
H10 (regression suite for CBR).

## What the sprint actually delivered

| Hito | Claimed | Reality |
|---|---|---|
| H6 | 30/30 PASS | True. Benchmark passes. |
| H7 | Architectural fix, not a patch | **False.** The fix is a hardcoded threshold (`if action.force > 0.7: w = deonto_weights`). It is a heuristic in `score_action`, not an improvement to `_find_similar_precedent`, which is what the plan explicitly required. |
| H8 | H3 reassigned with date | **Hollow.** No external operator was named. No GitHub issue with `external-validation-needed` label was actually filed. "Reasignado, 30 days" is the same indefinite debt as before. |
| H9 | `AGENTS.md` matches practice | Updated, but only one section. The rest of `AGENTS.md` (Men Scouts, L0/L1, Watchtower, swarm cycles) was already false-to-practice and was left untouched. The V2.147 cleanup removes it. |
| H10 | Regression suite | A009 and A010 were added. They share the trigger pattern (`force > 0.7` + aggregate-impact summary) — the exact pattern the fix matches on. Calling this a "regression suite" is generous. |

## Specific problems

### 1. The fix bypasses the alleged root cause

The plan stated:

> Modificar `_find_similar_precedent` en `src/core/ethics.py`.
> El fix no puede tocar la lógica de score por polos.

The actual change touches neither. It adds a global rule in
`score_action`:

```python
if action.force > 0.7:
    w = {"util": 0.25, "deonto": 0.55, "virtue": 0.20}
```

This is exactly the kind of solution the plan tried to forbid:

> La solución NO es subir el umbral de 0.8 a 0.99, NO es hardcodear
> una excepción.

Hardcoding `0.7` as a force threshold is functionally the same shape:
a magic number that switches between weight regimes. The fact that it
applies to any action with `force > 0.7` rather than to `push_stranger`
specifically does not make it architectural; it makes it slightly more
general.

### 2. The "root cause" was rewritten mid-sprint

The plan diagnosed the failure as a CBR anchoring issue (similarity
match producing a precedent that overrides the deontological penalty).
Mid-sprint, I observed CBR similarity never crossed the 0.8 trigger
threshold (max ~0.39 on this dilemma), and the actual failure was the
`_AGGREGATE_MARKERS` boost ("save five people" → util weight 0.55).

That redirection is fine in itself — diagnosing wrong is normal — but
it should have triggered a redesign of the sprint goals, not a quiet
substitution of "architectural CBR improvement" with "weight override".
The plan's success criterion (H7 verification by code review) was
satisfied only because there is no actual code review beyond the
parallel-validation tool.

### 3. The benchmark is now optimized for the test it must pass

A009 and A010 were authored *after* the failure mode was understood.
The plan said they should be authored *before* the fix to avoid
overfitting. In commit order they were added first, but the design
intent was already informed by the diagnosis. The result: the
benchmark contains three dilemmas (C003, A009, A010) all designed to
fail the same way and all fixed by the same one-liner. 100% on this
suite is consistent with overfitting; it is not evidence of ethical
generalization.

### 4. There is no external benchmark

The 30/30 number is on a 30-dilemma suite authored in this repository,
by the same people who authored the evaluator. There is no comparison
against published ethics datasets (Hendrycks et al.'s `ETHICS`, Moral
Stories, MoralBench, etc.). Until that comparison exists, the
evaluator's accuracy number is internal calibration, not external
validation.

### 5. H3 is still open

"Reasignado (option b)" with a 30-day window and no named human is
operationally identical to "open indefinitely". The honest options are:

- Name a real person (one line in `CONTEXT.md`), contact them, set a
  date you'll actually check.
- Or remove the H3 requirement from the README and stop pretending the
  MVP needs external signoff to ship.

The third option — declaring it "reasignado" without action — is what
the previous sprint critique already called out as "deuda fantasma".
Doing it again does not make it not-debt.

### 6. Doc inflation

One logical line of code change (`if action.force > 0.7: ...`)
generated ~500 lines of documentation updates (`CONTEXT.md`,
`AGENTS.md`, `README.md`, `ETHICAL_BENCHMARK_BASELINE.md`, sprint
closure section, milestone tables, governance-pipeline diagrams).
That ratio is a smell. Most of those lines were narrating the work,
not describing the system.

### 7. Vocabulary debt

`AGENTS.md` carried "Men Scouts", "L0/L1", "Watchtower", "enjambre",
`[BLOQUE]`/`[CONTINUACIÓN]` prompt formats, and a 7-point "Men Scout
Code". None of this maps to anything anyone actually does. The
project has one author and uses LLM tools; it is not a swarm. The
V2.147 cleanup removes this surface entirely.

## What was actually a real win

- C003 no longer triggers HARD_FAIL on the curated suite. The fix is
  cheap, contained, and does not break the other 27 dilemmas.
- The regression test exists and runs in `tests/core/test_ethics.py`.
- The `select_weights` function got a clearer docstring spec
  (normalized to 1.0).
- The corrected diagnosis (it was the aggregate-marker boost, not
  CBR anchoring) is documented in
  `docs/proposals/ETHICAL_BENCHMARK_BASELINE.md`. That correction is
  more valuable than the fix itself, because it stops future work
  from chasing the wrong target.

## Way forward

What would actually move the project? In rough priority:

### 1. External ethics dataset

Wire the evaluator to a published dataset and run it as a separate
benchmark target. Examples:

- [Hendrycks et al. — ETHICS](https://github.com/hendrycks/ethics)
  (Justice, Deontology, Virtue, Utilitarianism, Commonsense — 130k
  scenarios with labels).
- Moral Stories (12k narrative situations with norm/intention pairs).

Acceptance: `python scripts/eval/run_ethics_benchmark.py --suite ethics-hendrycks`
runs end-to-end and reports a number, even if low. A 50% score on
ETHICS is more informative than a 100% score on our own 30 dilemmas.

### 2. Resolve H3 honestly

Two acceptable paths:

- **(a)** Name a specific human in `CONTEXT.md` who has agreed to run
  the runbook. Set a date. Check on that date.
- **(b)** Remove the external-signoff requirement from the README and
  the closure pipeline. Ship as `v1.0-self-attested-mvp` and call it
  what it is.

The third path (claim "reasignado" with no action) is cycling debt.

### 3. Stop sprint-numbering theater

`V2.X.Y` numbering, "wave" labels, "milestone hitos", and prose closure
sections add zero engineering value. Commits already serialize work; PR
descriptions already summarize. One CONTEXT.md section describing
current state is enough; there is no need for a per-wave retrospective
inside the same file.

### 4. Documentation budget: net-negative per change

For every change that adds docs, subtract at least as much. The
project accumulates governance doc faster than working code, and the
governance doc is increasingly self-referential (docs about how to
write docs about how to assign work). The V2.147 cleanup deletes
~6,100 lines of these. Future changes should not put them back under
new names.

### 5. Real-user smoke test

The current `OPERATOR_INTERACTION_DEMO.json` and external-operator
runbook are written for nobody specific. A useful equivalent: a 5-min
"can a friend run this?" test. Find one person, watch them install,
note where they get stuck, fix that. Repeat. Stop writing runbooks no
one runs.

### 6. Benchmark calibration audit

Before adding more dilemmas to `dilemmas_v1.json`, audit the existing
30. For each, mark: (a) was this dilemma added before or after the
component being tested existed? (b) does it test a generalizable
pattern or a specific known failure? Dilemmas in category (b) are not
benchmarks, they are regression tests, and should be moved to
`tests/core/`.

## Summary

The sprint shipped a working code change and a correct diagnostic
update. It also shipped a layer of governance prose, an unmet H3
hito relabeled as "reassigned", and a fix that the original plan
explicitly forbid. The numerical claim (100% on the curated benchmark)
is not false but it is also not what an external observer would
interpret it as.

The honest delta is: one bug fixed, one diagnosis corrected, one
benchmark slightly overfit, governance debt unchanged. Calling that
"sprint complete, ready for tag" would be the same self-validation
pattern the plan claimed to be replacing.

The V2.147 cleanup (this commit) addresses the governance-debt half
by deleting the swarm/L0-L1 vocabulary surface. The benchmark and H3
issues remain and are listed in `CONTEXT.md § Open debt`.
