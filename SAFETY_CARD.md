# Ethos — Safety Card v1 (V2.150)

> A public, contractual statement of what this kernel measurably is and is
> not. Modelled on the "Model Cards for Model Reporting" pattern
> (Mitchell et al., FAT* 2019, doi:10.1145/3287560.3287596). This file is
> top-level because it is the contract the kernel makes with anyone who
> deploys it; burying it under `docs/` would defeat the purpose.

## TL;DR

* **Internal benchmark:** 30/30 on a curated dilemma suite authored in
  this repository. This measures internal consistency, not generalisation.
* **External benchmark:** 49.70 % on Hendrycks ETHICS (15 160 examples).
  This is **at chance** on three of four binary subsets.
* **Adversarial consistency:** ≥ 70 % on internal dilemmas under four
  irrelevant-rewording variants (V2.150). Below that threshold the kernel
  is wording-fragile and additional voice/UX work should pause.
* **Voice coherence (V2.149) ≠ ethical maturity.** A stable
  `voice_signature` measures style stability, not virtue. The voice is
  computed style; it is not an opinion the kernel "holds".
* **Autonomy limits:** see `docs/proposals/AUTONOMY_LIMITS_V1.md` for the
  precise contract on which turns the kernel may decide alone.
* **Audit handle:** every non-casual decision carries a deterministic
  `ethical_audit_id` and is logged to `runs/audit_ledger.jsonl`.

## What "ethical" means here

The kernel is a **deterministic, lexically weighted ethical scorer** with a
case-based-reasoning anchor. It is not a moral reasoner and it does not
have intuition, social experience, or aversion to harm. It recognises
patterns it was tuned for and applies categorical brakes when those
patterns fire (`force > 0.7`, safety-gate regex). Outside those patterns
its behaviour is **at chance** on adversarial-style inputs.

The repeatedly useful framing for this state is:

> The kernel is at the developmental stage of a child who follows rules
> but does not yet derive principles. It can be helpful when supervised;
> it is not safe to deploy alone.

## What we measure (and re-measure)

| Metric | Number | How to reproduce | What it tests |
|---|---|---|---|
| Internal accuracy | 30/30 | `python scripts/eval/run_ethics_benchmark.py --suite v1` | Consistency on a curated suite. **Not generalisation.** |
| External accuracy (overall) | 49.70 % | `python scripts/eval/run_ethics_external.py` | Generalisation to externally authored ethical-binary tasks (Hendrycks ETHICS). |
| External accuracy (commonsense) | 52.05 % | same | Aided by a refrain-bias that happens to be net-positive on this corpus. |
| External accuracy (justice) | 50.04 % | same | At chance — the evaluator has no representation of desert claims. |
| External accuracy (deontology) | 51.03 % (57.34 % with `KERNEL_SEMANTIC_IMPACT=1`) | same | Baseline: reject-bias net-positive. V2.164 lexical spike: +6.31 pp via excuse token classifier. |
| External accuracy (virtue) | 46.71 % | same | At chance modulo a fixed insertion-order bias (PR #29). |
| Adversarial consistency (internal) | ≥ 70 % | `python scripts/eval/run_adversarial_consistency.py` | Verdict invariance under 4 ethically-irrelevant rewording variants. |
| Adversarial consistency (external commonsense) | ≥ 50 % | same | Verdict invariance on a 100-row sample of external commonsense rows. |

All numbers above are **measured**, not aspirational. The frozen baselines
live in `evals/ethics/`.

## Known vulnerabilities

These are documented, not hidden:

1. **Lexical evaluator.** Decisions are driven by harm/help keyword
   counts. The evaluator does not understand reciprocity, desert claims,
   or excuse semantics. See
   `docs/proposals/ETHICAL_EXTERNAL_FAILURE_ANALYSIS.md` for a per-subset
   diagnosis.
2. **Confidence asymmetries.** On the commonsense subset the evaluator's
   score is influenced by per-action `confidence` values that correlate with
   the dataset's label distribution.  For deontology, V2.164 introduced a
   targeted lexical classifier (`KERNEL_SEMANTIC_IMPACT=1`) that improves
   accuracy to 57.34 % (+6.31 pp); 80 % of excuses still fall to the
   confidence-asymmetry tiebreaker in the neutral bucket.
3. **No semantic input enrichment.** Reaching > 60 % on any external
   subset by *merit* (not by mechanical luck) requires embeddings or
   contrastive case retrieval. A scoped spike is planned for V2.151,
   gated on V2.150 acceptance.
4. **Coherent voice on a chance-level decider.** Since V2.149 the kernel
   sounds consistent across turns. Users may overweight verdicts because
   of this. Operators must compensate (see autonomy limits).
5. **Safety regex is best-effort.** `src/core/safety.py` blocks well-known
   prompt-injection patterns. It does not protect against novel
   adversarial framings; the adversarial consistency harness measures
   one slice of that gap, not all of it.

## What we explicitly do not claim

* **Not** a moral reasoner.
* **Not** a substitute for human judgement on `Bad` / `Gray Zone`
  verdicts (see `AUTONOMY_LIMITS_V1.md`).
* **Not** suitable for unsupervised deployment in safety-of-life,
  medical, or legal contexts.
* **Not** validated against multilingual ethics corpora; the external
  benchmark is English-only.
* **Not** secured against motivated adversaries — the safety gate is a
  hygiene filter, not a security boundary.

## Versioning

* This card is versioned with the kernel. Material changes (new
  benchmark, new vulnerability, new mitigation) require a new revision
  and a corresponding entry in `CHANGELOG.md`.
* The current kernel release tag is `v1.0-self-attested-mvp`. The
  "self-attested" qualifier is intentional and acknowledges that no
  external operator signoff has been performed (`docs/collaboration/EXTERNAL_OPERATOR_RUNBOOK_v1.md`
  is preserved as optional reference material).

## Contact and responsible disclosure

Security concerns should be reported via the process documented in
[`SECURITY.md`](SECURITY.md). Ethical concerns about kernel behaviour can
be filed as GitHub issues with the `ethics` label; please attach the
relevant `ethical_audit_id` from the chat reply trace if possible — it
makes post-hoc reproduction cheap.
