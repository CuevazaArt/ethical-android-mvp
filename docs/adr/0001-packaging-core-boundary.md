# ADR 0001 — Pip-installable core vs monolith repo

**Status:** Proposed (April 2026)  
**Context:** [CRITIQUE_ROADMAP_ISSUES.md](../CRITIQUE_ROADMAP_ISSUES.md) Issue 4 — reviewers asked for a **documented boundary** between a thin **policy core** (MalAbs → scoring → poles → will) and optional **theater** (weakness, PAD, DAO mock, WebSocket stack).

## Decision

1. **Document first:** [`CORE_DECISION_CHAIN.md`](../CORE_DECISION_CHAIN.md) is the canonical map; [`pyproject.toml`](../../pyproject.toml) carries **stub** project metadata and optional dependency groups — **not** a claim of a published wheel on PyPI yet.
2. **Repository layout unchanged:** Python imports remain `from src.kernel import …` / `from src.modules…` until a dedicated refactor renames the installable package (e.g. `ethos_kernel`).
3. **CI source of truth:** `requirements.txt` remains what CI and contributors use today; `pyproject.toml` `[project.optional-dependencies]` mirrors it for experiments with `pip install -e ".[runtime]"` etc.
4. **Follow-up (out of scope here):** optional extraction of a **`ethos_kernel`** package with explicit `py.typed`, slimmer `install_requires`, and re-exports; landing / chat server may stay as an extra or separate repo.

## Consequences

- **Positive:** Clear ADR trail for partners asking “what would ship as a library?”
- **Negative:** `pip install -e .` may require setuptools to discover the flat `src/` tree; subpackages without `__init__.py` may need namespace configuration or small packaging fixes in a follow-up PR.

## Links

- [`CORE_DECISION_CHAIN.md`](../CORE_DECISION_CHAIN.md)  
- [`RUNTIME_CONTRACT.md`](../RUNTIME_CONTRACT.md)
