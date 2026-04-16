# Data governance policy (Ethos Kernel)

**Status:** Operator policy for self-hosted and lab deployments. This is **not** legal advice; align with your jurisdiction (GDPR, HIPAA, sector rules) before production use.

## 1. Roles- **Operator:** entity running the kernel process (developer, lab, organization).
- **End user:** person interacting via chat or API.
- **Telemetry backend:** Prometheus, log aggregators, or third parties (if any).

## 2. Data categories

| Category | Examples | Typical retention |
|----------|----------|-------------------|
| **Conversation content** | User messages, LLM replies | In RAM per WebSocket session unless persisted in checkpoints or logs. |
| **Checkpoints** | `KERNEL_CHECKPOINT_PATH` JSON/SQLite | Operator-defined; delete files to remove persisted state. |
| **Conduct guide export** | `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` | Operator-defined; may summarize episodes without raw text depending on config. |
| **Audit chain** | `KERNEL_AUDIT_CHAIN_PATH` JSONL | Append-only; retention = file rotation / archival policy (see [AUDIT_TRAIL_AND_REPRODUCIBILITY.md](AUDIT_TRAIL_AND_REPRODUCIBILITY.md)). |
| **Metrics** | Prometheus counters/histograms when `KERNEL_METRICS=1` | Scrape retention in your TSDB; labels must not carry raw user text. |
| **Structured logs** | `KERNEL_LOG_JSON=1` | Log pipeline retention; **do not** log full prompts unless explicitly approved. |

## 3. Encryption at rest

- **Checkpoints:** optional `KERNEL_CHECKPOINT_FERNET_KEY` (Fernet) for JSON checkpoints — see `src/persistence/json_store.py`.
- **SQLite:** not encrypted in the MVP; use OS-level disk encryption or an external secret wrapper for sensitive deployments.
- **Audit chain file:** not encrypted by the kernel; place on encrypted volumes or encrypt archives after rotation.

## 4. Deletion and user rights

This codebase is a **research kernel**, not a multi-tenant SaaS with built-in account deletion.

**Practical controls for operators:**

1. **Session-only:** avoid checkpoint path → state disappears when the process ends.
2. **Delete checkpoint / SQLite files** → removes serialized narrative, DAO mock state, and related fields.
3. **Truncate or delete audit chain** → breaks hash continuity; archive first if compliance requires history.
4. **Conduct guide export:** delete the file on disk.

For **right-to-erasure** requests, operators must map stored artifacts (paths above) and remove or anonymize them outside this repo’s automation.

## 5. Telemetry and consent

| Env | Meaning |
|-----|---------|
| `KERNEL_METRICS` | **Off by default.** When `1`, exposes `/metrics` (Prometheus). Inform users if scrapes leave the operator’s network. |
| `KERNEL_LOG_JSON` | Structured logs; scope what your log shipper indexes. |
| `KERNEL_CHAT_INCLUDE_*` | Toggles **payload fields** (e.g. monologue, user_model aggregates). Reduce surface area for privacy reviews. |

**Consent:** For any deployment where end users are not internal testers, document in your UI or terms: what is logged, metrics, retention, and who can access logs. The kernel does not render consent UI.

## 6. Third parties- **LLM providers** (Anthropic, local Ollama, HTTP adapters): prompts leave the operator’s host when using remote APIs — covered by provider DPAs, not this repo.
- **Codecov / CI:** follow GitHub secret hygiene; see [SECURITY.md](../SECURITY.md).

## 7. Related documents

- [AUDIT_TRAIL_AND_REPRODUCIBILITY.md](AUDIT_TRAIL_AND_REPRODUCIBILITY.md)
- [TRANSPARENCY_AND_LIMITS.md](TRANSPARENCY_AND_LIMITS.md)
- [KERNEL_ENV_POLICY.md](proposals/KERNEL_ENV_POLICY.md)
