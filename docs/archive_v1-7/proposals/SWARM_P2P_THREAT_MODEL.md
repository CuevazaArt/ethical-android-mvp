# Swarm / P2P ethical gossip — threat model (v9.3 stub)

**Status:** Design + **offline stub** (`src/modules/swarm_peer_stub.py`). **No** live mesh, **no** ZK proofs, **no** change to MalAbs → … → will. Cross-links [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) pillar 3.

## Purpose

Nomadic or co-located instances might exchange **compact, non-binding digests** of past verdicts to detect divergence under stress. This document states what the stub **does not** secure so operators do not mistake it for consensus or cryptography.

## Scope (stub)

| In scope | Out of scope |
|----------|----------------|
| Deterministic JSON + short SHA-256 fingerprint for a **single** episode summary fields | Bluetooth / Wi‑Fi / QUIC transports |
| Optional env `KERNEL_SWARM_STUB=1` to expose digest helpers in tooling/tests | Identity binding, Sybil resistance, replay protection on the wire |
| Pure-Python statistics over a **list of digests** supplied by the caller (lab harness) | Endorsement of actions, DAO weight, or “correct ethics” |

## Threat model (minimal)

1. **Malicious peer:** sends crafted digests — stub does not authenticate peers; **agreement_ratio** is descriptive only.
2. **Sybil:** many fake nodes — not addressed without identity layer (out of scope).
3. **Privacy:** digests include `episode_id`, `verdict`, `score`, `context` — operators must treat payloads as **sensitive** if episodes are sensitive; use hashing only for fingerprinting, not redaction.
4. **Kernel boundary:** nothing in `swarm_peer_stub` calls `EthicalKernel.process` or alters `final_action`.

## Non-goals

- Replacing lighthouse, DAO mock, or MalAbs.
- Proving moral correctness or legal compliance.

## Future work (not stub)

Pairwise channels, signed envelopes, rate limits, and explicit **operator consent** UX before any real P2P send.
