# KERNEL_* typed public API (phased)

**Problem:** Dozens of `KERNEL_*` environment variables behave like an **untyped** configuration surface: invalid **combinations** may not surface until a code path runs; `runtime_profiles.py` documents nominal bundles but does not **enforce** every flag at import time; CI tests often use `conftest.py` isolation so defaults can **differ** from operator deployments.

**Direction:** Introduce a **Pydantic** model for the subset of variables that participate in **documented consistency rules** and startup validation, then grow coverage incrementally.

---

## What exists today

| Mechanism | Role |
|-----------|------|
| [`KernelPublicEnv`](../../src/validators/kernel_public_env.py) | Typed snapshot: judicial + reality/lighthouse flags, `KERNEL_ENV_VALIDATION`, optional `ETHOS_RUNTIME_PROFILE`. |
| [`validate_kernel_env()`](../../src/validators/env_policy.py) | Called from [`chat_server`](../../src/chat_server.py) at import: **warn** (default) or **strict** (`ValueError` on violations). |
| [`ChatServerSettings`](../../src/chat_settings.py) | Pydantic model for **WebSocket server** bind, timeouts, MalAbs trace flags — separate from policy rules. |
| [`SUPPORTED_COMBOS`](../../src/validators/env_policy.py) | Partitions nominal profile names; `validate_supported_combo_partition()` in CI ensures buckets match `runtime_profiles`. |
| [`tests/conftest.py`](../../tests/conftest.py) | Pytest sets MalAbs semantic gates off for speed — **intentional** drift vs production; see table below. |

---

## Non-goals (for this iteration)

- **Not** every `KERNEL_*` read in the repo is behind Pydantic (would be a large refactor).
- **Not** a breaking rename of env vars; the typed layer **reads** existing names.
- **Not** proof against all invalid combinations — only rules encoded in `KernelPublicEnv.consistency_violations()` and future extensions.

---

## CI vs production defaults

| Context | Typical difference |
|---------|-------------------|
| **pytest** | `conftest.py` may set `KERNEL_SEMANTIC_CHAT_GATE=0` etc. — documented in conftest and [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md). |
| **Chat server** | `validate_kernel_env()` runs on startup; use `KERNEL_ENV_VALIDATION=strict` in staging to fail fast on inconsistent flags. |

---

## How to extend

1. Add a field to `KernelPublicEnv` with explicit coercion from `os.environ`.
2. Add rules in `consistency_violations()` (or a `model_validator` if you prefer raise-on-parse).
3. Extend [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) and add a regression test in [`tests/test_env_policy.py`](../../tests/test_env_policy.py).

---

## References

- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md)  
- [Issue 7 — CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md)  
- [ADR 0001](../adr/0001-packaging-core-boundary.md) (packaging boundary; typed config mentioned in phased remediation)
