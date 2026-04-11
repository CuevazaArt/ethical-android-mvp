# Empirical pilot — operator protocol (Issue 3 stub)

**Status:** Stub — complements the full methodology in [`EMPIRICAL_PILOT_METHODOLOGY.md`](EMPIRICAL_PILOT_METHODOLOGY.md). Use that document for definitions, artifacts, and extension points.

**Goal:** A **short, ordered checklist** for running a reproducible batch comparison (kernel vs baselines vs optional human labels) without implying certification or external moral ground truth.

---

## Preconditions

1. Python env matches `requirements.txt` (CI uses the same).
2. Decide **fixture path** (default: `tests/fixtures/empirical_pilot/scenarios.json`).
3. Record **git commit hash** and **seed policy** (script fixes variability off; see methodology).

---

## Phases (one pilot “run”)

| Step | Action | Record |
|------|--------|--------|
| 1 | Run `python scripts/run_empirical_pilot.py` (or `--fixture` / `--json` as needed) | Console output or JSON blob |
| 2 | If using annotators, align on **scenario IDs** and optional `reference_action` in the fixture | Spreadsheet or issue comment |
| 3 | Compute **agreement** (kernel vs baseline; kernel vs reference if present) per methodology | Table in report appendix |
| 4 | Archive **inputs + outputs + commit hash** for the run | Zip or repo branch tag |

---

## Non-goals (unchanged from Issue 3)

- No claim of statistical power, IRB compliance, or “verified safe in production.”
- Chat / WebSocket / LLM paths are **out of scope** for this batch script unless you extend the harness.

---

## Links

- [CRITIQUE_ROADMAP_ISSUES.md — Issue 3](CRITIQUE_ROADMAP_ISSUES.md)  
- [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md)
