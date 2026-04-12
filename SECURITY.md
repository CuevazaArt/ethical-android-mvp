# Security policy

## Scope

This repository contains a **research prototype** (Python kernel, tests, static dashboard, Next.js marketing site). Reports are welcome for issues that affect **users of this software** or **repository integrity** (e.g. supply chain, secrets in history, XSS on the landing if applicable).

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

## Supported versions

Security fixes, when provided, apply to the **default branch** (`main`) going forward. Tags or releases may not exist; pin to a commit for deployments.

## Secrets and local configuration

- Do **not** commit `.env`, raw Fernet keys, or third-party API tokens. Copy [`.env.example`](.env.example) to a local `.env` (gitignored) if your tooling loads it.
- **GitHub Actions:** add sensitive values only as **encrypted repository secrets** (or environment secrets), not in workflow YAML. Optional third-party integrations (for example Codecov) use a `CODECOV_TOKEN` secret when enabled by maintainers.

## Kernel input trust (MalAbs + LLM perception)

- **MalAbs chat gate** (`AbsoluteEvilDetector.evaluate_chat_text`) uses **conservative substring lists** after Unicode normalization — **not** unbreakable filtering. Paraphrase and novel jailbreaks can slip through; see [`docs/proposals/INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md). The same gate runs on **`process_natural`** input before perception. **Optional:** `KERNEL_SEMANTIC_CHAT_GATE=1` adds Ollama **embeddings** after lexical matching, with optional **LLM arbiter** for ambiguous bands — see [`docs/proposals/MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md); not a guarantee.
- **LLM perception JSON** is **clamped and validated** (`perception_from_llm_json` in `src/modules/llm_layer.py`); non-object JSON is ignored. Garbage-in / prompt-injection can still skew signals within \([0,1]\); the kernel does not treat numeric outputs as ground truth.

## Hardening in this repo (landing + dashboard)

- **HTTP headers (Next.js middleware):** `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, path-specific **Content-Security-Policy** (stricter for the main app; dashboard allows `https://unpkg.com` for pinned vendor scripts). **No `X-Frame-Options: SAMEORIGIN`:** it breaks Vercel’s in-dashboard deployment preview (parent `vercel.com` vs child `*.vercel.app`). **Clickjacking** is mitigated with **`frame-ancestors 'self' https://vercel.com`**, which still blocks arbitrary third-party embeds. **HSTS** and **CSP `upgrade-insecure-requests`** run when `VERCEL_ENV=production` (or set `FORCE_HSTS=1` for self‑hosted HTTPS), not on local `next dev` / Vercel preview.
- **`dashboard.html`:** React, ReactDOM, and `@babel/standalone` are loaded from **version-pinned** unpkg URLs with **Subresource Integrity** (`integrity="sha384-…"`) and `crossorigin="anonymous"`. If you bump a version, recompute the hash (e.g. `openssl dgst -sha384 -binary` on the file, then base64) or use [SRI Hash Generator](https://www.srihash.org/) against the exact URL.
- **Known residual risk:** Babel still compiles JSX in the browser, so the dashboard CSP retains `'unsafe-inline'` and `'unsafe-eval'` for that document. Eliminating that requires a pre-built JS bundle instead of `type="text/babel"`.
