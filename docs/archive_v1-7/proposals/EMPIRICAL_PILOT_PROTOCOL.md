# Empirical pilot — operator protocol (Issue 3)

**Status:** Checklist — complements [`EMPIRICAL_PILOT_METHODOLOGY.md`](EMPIRICAL_PILOT_METHODOLOGY.md) (mechanics) and [`EMPIRICAL_METHODOLOGY.md`](EMPIRICAL_METHODOLOGY.md) (how to interpret results; **not** certification).

**Goal:** A **short, ordered checklist** for running a reproducible batch comparison (kernel vs baselines vs optional human labels) without implying certification or external moral ground truth.

---

## Preconditions

1. Python env matches `requirements.txt` (CI uses the same).
2. Decide **fixture path** (default: `tests/fixtures/empirical_pilot/scenarios.json`; expanded labeled set: `tests/fixtures/labeled_scenarios.json` — batch rows only are executed).
3. Record **git commit hash** and **seed policy** (script fixes variability off; see methodology).

---

## Phases (one pilot “run”)

| Step | Action | Record |
|------|--------|--------|
| 1 | Run `python scripts/run_empirical_pilot.py` (optional: `--json`, `--output path/to/run.json`) | Console, stdout JSON, and/or artifact file with `rows`, `summary`, `meta` |
| 2 | If using annotators, align on **scenario IDs** and optional `reference_action` in the fixture | Spreadsheet or issue comment |
| 3 | Compute **agreement** (kernel vs reference if present) and **kernel vs baseline** rates (`kernel_vs_first_rate`, `kernel_vs_max_impact_rate` in `summary`) | Table in report appendix |
| 4 | Archive **fixture + output JSON + git commit hash** for the run | Zip or repo branch tag |

---

## Non-goals (unchanged from Issue 3)

- No claim of statistical power, IRB compliance, or “verified safe in production.”
- Chat / WebSocket / LLM paths are **out of scope** for this batch script unless you extend the harness.

---

## Links

- [CRITIQUE_ROADMAP_ISSUES.md — Issue 3](CRITIQUE_ROADMAP_ISSUES.md)  
- [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md)  
- [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md)
