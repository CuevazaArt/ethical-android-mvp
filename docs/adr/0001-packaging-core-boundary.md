# ADR 0001 — Pip-installable core vs monolith repo

**Status:** Accepted (April 2026)  
**Context:** [CRITIQUE_ROADMAP_ISSUES.md](../proposals/CRITIQUE_ROADMAP_ISSUES.md) Issue 4 — reviewers asked for a **documented boundary** between a thin **policy core** (MalAbs → scoring → poles → will) and optional **theater** (weakness, PAD, DAO mock, WebSocket stack).

## Decision

1. **Document first:** [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md) is the canonical map; [`pyproject.toml`](../../pyproject.toml) carries project metadata and optional dependency groups — **not** a claim of a published wheel on **PyPI** while `version` is `0.0.0`.
2. **PyPI / `pip install ethos-kernel`:** **Out of scope** as a shipping goal until semver, naming, and optional package rename (`ethos_kernel` import path) are decided. **Supported today:** editable install from a **Git clone** — `pip install -e .`, `pip install -e ".[runtime]"`, optional marker `pip install -e ".[theater]"` (no extra deps; documents the theater boundary). **`[project.scripts]`:** `ethos` → `src.ethos_cli:main`; `ethos-runtime` → `src.chat_server:main` (ASGI chat server when `[runtime]` extras are installed).
3. **Repository layout unchanged:** Python imports remain `from src.kernel import …` / `from src.modules…` until a dedicated refactor renames the installable package.
4. **CI source of truth:** `requirements.txt` remains what CI and contributors use today; `pyproject.toml` `[project.optional-dependencies]` mirrors extras for `pip install -e ".[…]"` experiments.
5. **Core vs theater:** **Not** split at import time in this iteration. Base `[project.dependencies]` match the policy path; narrative/DAO/PAD live in the same `src/` tree. The **`theater`** extra is an empty marker for integrators who want pip metadata to reflect that boundary (see README).
6. **Follow-up (out of scope here):** optional extraction of a **`ethos_kernel`** package with explicit `py.typed`, slimmer `install_requires`, and re-exports; landing / chat server may stay as an extra or separate repo.

## Consequences

- **Positive:** Clear ADR trail for partners asking “what would ship as a library?” and honest **research-only** posture vs PyPI.
- **Negative:** `pip install -e .` may require setuptools to discover the flat `src/` tree; subpackages without `__init__.py` may need namespace configuration or small packaging fixes in a follow-up PR.

## Links

- [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md)  
- [`RUNTIME_CONTRACT.md`](../proposals/RUNTIME_CONTRACT.md)
