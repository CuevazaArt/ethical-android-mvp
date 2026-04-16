# Security policy

## Scope

This repository contains a **research prototype** (Python kernel, tests, static dashboard). Reports are welcome for issues that affect **users of this software** or **repository integrity** (e.g. supply chain, secrets in history, XSS in static HTML if applicable).

## How to report

### Preferred: GitHub private vulnerability reporting

Use **Report a vulnerability** for this repository (GitHub shows it under the **Security** tab when [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/about-privately-reporting-a-security-vulnerability) is enabled).

**Repository maintainers:** enable it under **Settings → Code security → Private vulnerability reporting**.

### If private reporting is not available

1. Open a **public** Issue with the title prefix `[SECURITY]` and **do not** include exploit details, payloads, or customer data.
2. Ask for a **private channel** in the body; maintainers will follow up (e.g. email or GitHub-only thread as appropriate).

Do not use the generic “Funding, partnership, or press” template for undisclosed vulnerabilities.

## What to expect

- We aim to acknowledge receipt within a few business days when capacity allows.
- We may coordinate a fix and advisory depending on severity and impact.
- This project is maintained on a **best-effort** basis; there are no commercial SLAs.

## Out of scope (examples)

- Spam, social engineering, or denial-of-service against demo infrastructure unless you have a minimal reproducible report agreed in advance.
- Theoretical flaws in the **ethical model** or philosophy without a concrete software impact (use Issues / Discussions for research debate).
- **On-chain governance:** [`src/modules/mock_dao.py`](src/modules/mock_dao.py) is an **in-process simulation** (quadratic voting, audit strings). There is **no** deployed smart-contract product in this repository; a **non-functional** Solidity stub lives under [`contracts/`](contracts/README.md) for transparency only — see [`MOCK_DAO_SIMULATION_LIMITS.md`](docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md). Do not treat DAO UX as tamper-proof consensus or as the same thing as the kernel’s MalAbs / scoring policy path.

## Supported versions

Security fixes, when provided, apply to the **default branch** (`main`) going forward. Tags or releases may not exist; pin to a commit for deployments.

## Secrets and local configuration

- Do **not** commit `.env`, raw Fernet keys, or third-party API tokens. Copy [`.env.example`](.env.example) to a local `.env` (gitignored) if your tooling loads it.
- **GitHub Actions:** add sensitive values only as **encrypted repository secrets** (or environment secrets), not in workflow YAML. Optional third-party integrations (for example Codecov) use a `CODECOV_TOKEN` secret when enabled by maintainers.

## Kernel input trust (MalAbs + LLM perception)

**LLM-specific risks (summary):** Untrusted user text and untrusted model outputs are both in scope. Lexical filters do **not** provide semantic understanding; structured perception can be **valid but misleading** (values in range, wrong summary). Do not deploy this stack as a standalone safety boundary for high-stakes abuse without additional controls. See [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md) and the **hardening plan** in [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md). Automated cases: [`tests/adversarial_inputs.py`](tests/adversarial_inputs.py) (evasion) and [`tests/test_input_trust.py`](tests/test_input_trust.py) (normalization regressions).

- **MalAbs chat gate** (`AbsoluteEvilDetector.evaluate_chat_text`) uses **conservative substring lists** after Unicode normalization — **not** unbreakable filtering. Paraphrase, homoglyphs, leetspeak, and novel jailbreaks can slip through; see [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md). The same gate runs on **`process_natural`** input before perception. **Optional:** `KERNEL_SEMANTIC_CHAT_GATE=1` adds Ollama **embeddings** after lexical matching, with optional **LLM arbiter** for ambiguous bands — see [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md); not a guarantee.
- **LLM perception JSON** is **clamped and validated** (`perception_from_llm_json` in `src/modules/llm_layer.py`); non-object JSON is ignored. Prompt-injection or compromised models can still push hostility/risk/calm within \([0,1]\) coherently enough to bias downstream heuristics; the kernel does not treat numeric outputs as ground truth.
- **Integration backlog (LLM touchpoints, embeddings, degradation):** [`docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md) (gap register G-01…G-10).

## Audit chain (optional)

Operators can enable an **append-only** JSONL log of chat safety blocks (hash-linked lines, optional HMAC) via `KERNEL_AUDIT_CHAIN_PATH` — see [`docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md`](docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md). This does **not** replace centralized logging, SIEM review, or key management policy; it is a reproducibility aid for local audits.
