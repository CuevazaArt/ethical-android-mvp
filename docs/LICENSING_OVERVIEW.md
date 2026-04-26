# Licensing Overview — Ethos / Mos Ex Machina

> Last updated: 2026-04-26. Authoritative source: [`LICENSING_STRATEGY.md`](../LICENSING_STRATEGY.md).

This document is a quick-reference summary of the **dual-license model** used by the Ethos project.
For the full normative text, see [`LICENSING_STRATEGY.md`](../LICENSING_STRATEGY.md).

---

## License map at a glance

| Layer | Scope | License |
|-------|-------|---------|
| **Kernel + Server** | `src/core/`, `src/server/`, `src/ethos_cli.py`, `src/main.py`, `src/chat_server.py` | Apache 2.0 |
| **Tests & CI** | `tests/`, `scripts/` | Apache 2.0 |
| **Documentation** | `docs/`, `AGENTS.md`, `CONTEXT.md`, `CONTRIBUTING.md`, `BIBLIOGRAPHY.md`, `SECURITY.md` | Apache 2.0 |
| **Nomad Android SDK** | `src/clients/nomad_android/` | BSL 1.1 → Apache 2.0 after 36 months |
| **Fine-tuned models** | LoRAs, personality adapters, identity modules | Proprietary |
| **Cloud services** | Hosted inference, identity sync, SaaS nodes | Proprietary (SaaS) |
| **Brand** | "Mos Ex Machina", "Ethos", "Nomad", logos | Trademark — see [`TRADEMARK.md`](../TRADEMARK.md) |

---

## Apache 2.0 (open layers)

- **Allows:** use, modify, distribute, sublicense, commercial use.
- **Requires:** attribution, notice of changes, patent-clause compliance.
- License text: [`LICENSE`](../LICENSE) (root of repository).

## Business Source License 1.1 (Nomad Android SDK)

- **Non-production use:** free (research, education, personal projects, evaluation).
- **Production / commercial use:** requires a commercial license for the first **36 months** after each individual version's release date (the timer resets per-version, not per-SDK).
- **Auto-conversion:** each version automatically becomes **Apache 2.0** 36 months after its release.
- License text: [`src/clients/nomad_android/LICENSE_BSL`](../src/clients/nomad_android/LICENSE_BSL).

## Proprietary (models and hosted services)

- No source or weight access.
- Distributed as API / binary under a separate subscription or pay-once commercial agreement.

## Trademark

- **"Mos Ex Machina"**, **"Ethos"**, **"Nomad"** are trademarks of Juan Cuevaz / Mos Ex Machina.
- Commercial use of the marks requires written permission.
- Full policy: [`TRADEMARK.md`](../TRADEMARK.md).

---

## Contributor License Agreement (DCO)

Every contribution to this repository requires a **Developer Certificate of Origin** sign-off:

```
git commit -s -m "your commit message"
```

This adds `Signed-off-by: Your Name <email@example.com>` to the commit.

- Contributions to `src/core/` and all Apache 2.0 layers remain Apache 2.0.
- Contributions to `src/clients/nomad_android/` fall under BSL 1.1.

---

## Industry precedents

This hybrid model follows proven patterns:

| Project | Model |
|---------|-------|
| MariaDB | BSL → GPL |
| CockroachDB | BSL → Apache 2.0 after 3 years |
| HashiCorp Terraform | BSL for commercial, MPL for community |

---

For questions on commercial licensing or trademark use, contact [contact@mosexmachina.org](mailto:contact@mosexmachina.org).
