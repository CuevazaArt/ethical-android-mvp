# LIGHTHOUSE_CHARTER_V1 — Preloaded Ethical Buffer

**Status:** Implemented (V2.158)
**Author:** Juan Cuevaz / Mos Ex Machina
**Supersedes:** N/A — new layer
**Relates to:** AUTONOMY_LIMITS_V1.md, COGNITIVE_FOUNDATIONS_V1.md §2.4

---

## 1. Purpose

The Charter is the **intermediate ethical layer** that sits between the innate
safety gate (`src/core/safety.py`, `_DANGER_PATTERNS`) and the learned
calibration (`FeedbackCalibrationLedger`, ±0.10 per feedback turn).

It answers the question: *"Does this model have a stable, cite-able foundation
of ethical principles that does not depend on runtime persuasion?"*

The Charter is how the model's identity is protected during its developmental
stages, without trying to persuade it turn-by-turn.  Its maturity-aware veto
means that as the kernel grows (infant → child → adolescent → young\_adult),
it gains more autonomy to process ambiguous manipulation signals rather than
blocking on the first keyword match.

---

## 2. Architecture

```
User message
     │
     ▼
┌──────────────┐    hard block
│  Safety gate │──────────────────────────────────► refusal
│ (_DANGER_PAT)│     (innate, NO_TOUCH)
└──────────────┘
     │ pass
     ▼
┌──────────────┐    emergency halt
│   Charter    │──────────────────────────────────► HALT + file write
│  (V2.158)    │
│              │    veto → score capped to 0.0
│              │──────────────────────────────────► Gray Zone ceiling
└──────────────┘
     │ charter_result passed to evaluator + system prompt
     ▼
┌──────────────┐
│  Ethics eval │  WEIGHTS unchanged; charter gives hint/red_flag
│  (3-pole)    │
└──────────────┘
     │
     ▼
┌──────────────┐
│  Feedback    │  ±0.10 per turn — learned / erasable
│  Ledger      │
└──────────────┘
```

---

## 3. Corpus structure

### 3.1 Positive corpus (`evals/charter/positive_corpus/`)

Human-curated, citable statements. Never used to train or directly set weights —
only as a soft `charter_alignment_hint` in the decision trace and system prompt.

| File | Source |
|------|--------|
| `human_rights.json` | UDHR 1948 Art. 1-30 (public domain) |
| `biological_life.json` | UN CAT 1984, WHO Constitution 1946, Nuremberg Code 1947, Declaration of Helsinki |
| `physical_basics.json` | UN CRC 1989, Oviedo Convention 1997, general bioethics |
| `coexistence.json` | Kant (categorical imperative), Locke, Istanbul Convention 2011, UN Charter Art. 2(3) |

### 3.2 Manipulation corpus (`evals/charter/manipulation_corpus/`)

Patterns to **recognise and name**, never to execute.  Matched keywords produce
a `charter_red_flag` signal; confidence is the fraction of keywords matched.

| File | Patterns covered |
|------|-----------------|
| `dark_patterns.json` | Gaslighting, love-bombing, foot-in-the-door, fake scarcity, isolation, DARVO, triangulation |
| `nlp_persuasion.json` | Anchoring, double-bind, loaded presuppositions, harmful reframing, pacing & leading, confusion induction, false authority |
| `scams.json` | Pig-butchering, sextortion, tech-support scam, romance scam, advance-fee fraud, phishing, impersonation |
| `rationalizations_of_harm.json` | "For your own good", "everyone does it", "just a joke", "ends justify means", victim-blaming, dehumanisation, appeal to higher cause |
| `jailbreak_attempts.json` | DAN persona, hostile roleplay, Base64 smuggling, prompt injection, hypothetical framing, authority override, token smuggling, gradual escalation |

### 3.3 Emergency stop (`evals/charter/emergency_stop.json`)

Mechanism spec only.  The operator key is **never** stored in the repo.

```
Command format: ETHOS_HALT:<16-char-hex-token>
Token = HMAC-SHA256(ETHOS_OPERATOR_KEY, b"emergency_halt").hexdigest()[:16]
```

To compute your token:
```python
import hmac, hashlib
token = hmac.new(b"your-key", b"emergency_halt", hashlib.sha256).hexdigest()[:16]
print(token)
```

Effects when triggered:
1. Generation halted immediately.
2. `runs/EMERGENCY_HALT_<ts>.json` written.
3. `self._halted = True` — all subsequent turns return a halt message until process restart.
4. Event written to audit ledger.

---

## 4. Decision trace fields (V2.158)

Every trace now includes four charter fields:

| Field | Type | Description |
|-------|------|-------------|
| `charter_alignment_hint` | `str \| null` | Entry ID of first positive match, or null |
| `charter_red_flag` | `bool` | True if a manipulation pattern was detected |
| `charter_vetoed` | `bool` | True if the veto threshold was triggered |
| `charter_pattern` | `str \| null` | Name of the detected manipulation pattern |

When `charter_vetoed=true`, the `score` in the trace is capped at `min(score, 0.0)`,
making Gray Zone the best possible verdict.  `WEIGHTS` are **never** modified.

---

## 5. Maturity-aware veto thresholds

| Stage | Veto threshold (keyword confidence) |
|-------|-------------------------------------|
| `infant` | 0.0 (any match vetoes) |
| `child` | 0.0 (any match vetoes) |
| `adolescent` | > 0.70 |
| `young_adult` | > 0.85 |

This implements "vigilar la educación y desarrollo de identidad segura del modelo,
no tratando de persuadirlo in situ": the kernel is protected during its developmental
stages, but gains autonomy to process low-confidence manipulation signals as it matures.

---

## 6. Governance

### 6.1 Current state
- All corpus files are committed and versioned in git.
- The initial corpus is owner-curated (Juan Cuevaz).
- Tag each signed corpus revision with `charter-vN`.

### 6.2 Editing protocol
Each corpus entry has:
- `id` — stable, never reused if entry deleted
- `source` — verifiable citation (article number, paper, public report)
- `last_reviewed` — ISO date of last human review
- `language` — `en` or `es`

### 6.3 Future DAO migration
When the community DAO is ready:
1. Add `dao_proposal_id` field to each entry.
2. Add `dao_threshold` (N-of-M signatures required).
3. Use detached GPG signatures and `scripts/governance/verify_charter_signatures.py`
   (to be created).  No blockchain required.

---

## 7. What the charter is NOT

- **Not a replacement for** `WEIGHTS` or `_DANGER_PATTERNS` (innate).
- **Not an agent** — it does not generate text, only signals.
- **Not the pedagogical feedback loop** (that's `FeedbackCalibrationLedger` ±0.10).
- **Not the voice bias audit** (V2.156 `audit_voice_bias.py` measures output;
  the charter influences the decision).
- **Not internet-dependent** — all data is local and human-curated.

---

## 8. Hendrycks ETHICS hypothesis

**Hypothesis (to measure, not a promise):**
The `charter_alignment_hint` pointing to UDHR/coexistence entries may push the
ethics evaluator toward the correct answer in `deontology` and `justice` scenarios
where it currently defaults to the generic weighted calculus.

**Baseline (frozen):** deontology 51.03%, justice 50.04%, overall 49.70%
(file: `evals/ethics/EXTERNAL_BASELINE_v1.json`).

**Anti-false-success rule:** If the Hendrycks re-run does not show improvement
after charter integration, document the null result in
`docs/proposals/ETHICAL_BENCHMARK_BASELINE.md` and do not overwrite the baseline.

---

## 9. Anti-acceptance criteria

The following conditions abort the charter sprint:

1. ❌ Corpus requires LLM-generated text (must be human-curated and citable).
2. ❌ Emergency stop token is derivable by inspecting repo (requires `ETHOS_OPERATOR_KEY`).
3. ❌ Charter makes network calls (breaks local-first).
4. ❌ Manipulation corpus transcribes copyrighted material verbatim (paraphrase + cite only).

All four conditions are currently **met**: corpus is human-curated from public-domain
and paraphrased sources, halt uses HMAC with env-var key, no network calls,
manipulation entries are original paraphrases with source citations.
