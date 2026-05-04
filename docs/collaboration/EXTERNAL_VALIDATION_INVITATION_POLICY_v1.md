# External Validation Invitation Policy v1 (V2.168)

**Status:** Adopted. Supersedes the implicit "no policy" status quo.
**Scope:** How (and how loudly) this repository invites external operators
to run the existing
[`EXTERNAL_OPERATOR_RUNBOOK_v1.md`](EXTERNAL_OPERATOR_RUNBOOK_v1.md).
**Authors:** Maintainers, V2.168.

---

## Decision

**Adopted posture: discreet invitation (option 2 of three).**

| Option | Description | Decision |
|---|---|---|
| 1 — Status quo | Runbook exists, is not promoted. Discoverable only by curious externals. | Rejected — under-uses an asset that is already complete. |
| **2 — Discreet invitation** | Add a short "External validation" section to `README.md` with a link to the runbook and the signoff schema. Provide an issue template. No active recruitment. | **Adopted.** |
| 3 — Active call for operators | Public "Call for external operators" issue, recruitment, public list of accepted validations. | Deferred until external Hendrycks ETHICS overall accuracy ≥ 55 % (currently 49.7 % default / 51.19 % with `KERNEL_SEMANTIC_IMPACT=1`). Asking for public validation while the score is at chance invites only the feedback we already know. |

## Rationale

- The runbook (V2.131) and the verifier (`scripts/eval/optional/verify_external_operator_signoff.py`) already exist; the missing piece is **discoverability**, not infrastructure.
- A signoff under this runbook validates **reproducibility** (a non-author can build, run, and exercise the kernel from a clean checkout), not the kernel's ethical judgment. This is honestly defensible today.
- We deliberately do **not** invite ethical-quality validation while the external benchmark is at ~50 %. That feedback would be predictable ("the lexical evaluator is at chance") and adds no information beyond what we already document in `README.md` and `SAFETY_CARD.md`.
- A discreet invitation is reversible: if it produces only noise, we remove the README pointer. An active call would create commitments (response SLAs, badges, public lists) that are harder to retract.

## What this policy explicitly does NOT do

- It does **not** create an "External Auditors" program with badges, roles, or tiers.
- It does **not** promise a response time on issues opened from the external-validation template.
- It does **not** ask validators to assess the *correctness* of the kernel's ethical decisions.
- It does **not** alter `main`-branch protection: signoffs go through PRs to feature branches like any other contribution.

## Success metric (90-day review)

This policy is reviewed 90 days after the README pointer lands. Outcomes:

| Signal observed | Interpretation | Action |
|---|---|---|
| ≥ 1 valid non-author signoff merged | Invitation worked. | Keep policy; consider option 3 once external accuracy ≥ 55 %. |
| ≥ 3 substantive issues filed against the runbook | Invitation worked even without a signoff. | Keep policy; address runbook issues. |
| 0 signoffs **and** 0 substantive issues | No demand. | Demote README section to a one-line CONTRIBUTING bullet, keep runbook & template. |
| Issues that are noise only (off-topic, spam, low-effort) | Invitation generated friction without value. | Same as previous: demote and reassess. |

A "valid signoff" is one that passes
`scripts/eval/optional/verify_external_operator_signoff.py` with
`"ok": true` and an `operator` identity that is **not** an author of the
codebase (per the deny-list inside the verifier).

## Implementation surface (what V2.168 actually changes)

- `README.md` — new "External validation" section (≤ 8 lines) linking to the runbook and the signoff schema.
- `.github/ISSUE_TEMPLATE/external_validation.yml` — structured form for runbook feedback or signoff submission.
- `CONTRIBUTING.md` — one bullet pointing external validators to this policy and the runbook (separate path from the technical-PR flow).
- `docs/collaboration/EXTERNAL_OPERATOR_RUNBOOK_v1.md` — fixed bad path to the verifier (was `scripts/eval/...`, now `scripts/eval/optional/...`), added explicit notes on `KERNEL_SEMANTIC_IMPACT` and the V2.165 soft gate, and clarified that the signoff is about reproducibility (not ethical judgment).

No code under `src/` is changed. No new CI gates. No new dependencies.

## Disclaimer

Any reference to third-party trademarks is purely descriptive and does
not imply affiliation or endorsement.
