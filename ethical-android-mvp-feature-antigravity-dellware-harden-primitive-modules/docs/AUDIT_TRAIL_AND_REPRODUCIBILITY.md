# Audit trail and reproducibility

## Goals

1. **Append-only** records for safety-critical events (MalAbs block, optional kernel block).
2. **Hash chain** so tampering with past lines breaks verification (Merkle-style continuity per line).
3. **Optional HMAC** with an operator-held secret to show origin authenticity (not non-repudiation against users; useful for internal audits).
4. **No PII by default** in payloads (category, `decision_trace`, hashes of reason text).

## Implementation

Module: [`src/modules/audit_chain_log.py`](../src/modules/audit_chain_log.py)

| Env | Purpose |
|-----|---------|
| `KERNEL_AUDIT_CHAIN_PATH` | Filesystem path to a JSONL file (created if missing). Empty = feature off. |
| `KERNEL_AUDIT_HMAC_SECRET` | Optional shared secret; if set, each line gets an `hmac_sha256` over the **canonical JSON** of the line fields **excluding** `line_sha256` and `hmac_sha256` (same string used to compute `line_sha256`). |
| `KERNEL_AUDIT_INCLUDE_REASON_HASH` | Default on: store `reason_sha256` only. Set to `0` to omit (not recommended for audits). |

Each JSON line (one object) contains:

- `seq` — monotonic counter.
- `ts_unix` — Unix time (float).
- `event_type` — e.g. `malabs_chat_block`, `kernel_chat_block`.
- `payload` — structured fields (no raw user text); must match `payload_sha256`.
- `payload_sha256` — SHA-256 of the canonical JSON of `payload` alone (sorted keys).
- `prev_line_sha256` — SHA-256 of the previous line’s canonical core fields (genesis: all-zero hex).
- `line_sha256` — SHA-256 of the canonical object **without** `line_sha256` and **without** `hmac_sha256`.
- `hmac_sha256` — optional.

**Verification (external tool or notebook):** read JSONL in order; recompute each `line_sha256` and `prev_line_sha256` link; verify HMAC if secret available.

## Relationship to MockDAO audit

[`MockDAO.register_audit`](../src/modules/mock_dao.py) keeps in-memory **audit records** for demos and snapshots. The **audit chain log** is a separate, filesystem-backed trail for **immutability** and export. You may correlate by timestamp or future `correlation_id` if added.

## Digital signatures (roadmap)

Ed25519 or RSA line signatures per record require key management (HSM, KMS). The current design uses **hash chain + optional HMAC** as a lightweight step. Upgrade path: add `signing_key_id` + `signature` fields and verify offline.

## Related

- [GOVERNANCE_DATA_POLICY.md](GOVERNANCE_DATA_POLICY.md)
- [TRANSPARENCY_AND_LIMITS.md](TRANSPARENCY_AND_LIMITS.md)
