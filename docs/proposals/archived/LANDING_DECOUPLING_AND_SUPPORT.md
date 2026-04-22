# Landing (Next.js) — decoupling, support level, and CI (April 2026)

**Purpose:** State clearly how the **`landing/`** Next.js app relates to the **Python Ethos Kernel**, what is **officially supported** in this monorepo, and how **versioning**, **SEO**, and the **interactive dashboard** are kept coherent.

---

## 1. Support stance: official, but not the runtime

| Layer | Role in this repository |
|--------|---------------------------|
| **`src/` (Python)** | **Primary** product and research artifact: MalAbs → Bayes → poles → will, FastAPI WebSocket server, tests, ADRs. |
| **`landing/`** | **Officially supported** as the **public marketing / education** surface: Next.js site, theory pages, **optional** deploy (e.g. Vercel). It is **not** required to run, test, or operate the kernel. |

**Branding vs core:** The landing is **more than a stray folder**: it is maintained in-tree (Apache-2.0), with its own CI (`.github/workflows/landing-ci.yml`). It does **not** ship the ethical decision core; it links to the repo and embeds demos.

**Not implied:** Using the marketing site does **not** mean the kernel is “certified” for any production domain; see [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) and [TRANSPARENCY_AND_LIMITS.md](../TRANSPARENCY_AND_LIMITS.md).

---

## 2. Separate `npm` install (by design)

Contributors working **only** on Python can ignore `landing/`. Those changing the site:

```bash
cd landing
npm ci
npm run dev
```

`npm install` at repo root is **not** used; the Node graph lives under `landing/package.json`.

---

## 3. Version sync (kernel vs landing app)

| Value | Source | Exposed on site |
|--------|--------|-----------------|
| **Kernel library semver** | Root [`pyproject.toml`](../../pyproject.toml) `[project].version` | `landing/src/config/kernelRepo.json` → footer on the home landing (`Kernel package …`) |
| **Landing app semver** | [`landing/package.json`](../../landing/package.json) `version` | Same JSON → `landing app …` |

**Regeneration:** From `landing/`:

```bash
npm run sync-kernel-meta
```

Commit the updated **`landing/src/config/kernelRepo.json`**. **Landing CI** runs `sync-kernel-meta` and **`git diff --exit-code`** on that file so a bump to `pyproject.toml` without regenerating the JSON **fails** the workflow.

**Vercel / subdirectory-only deploy:** If the build context is **`landing/`** and the parent `pyproject.toml` is **not** present, set **`NEXT_PUBLIC_KERNEL_PYPROJECT_VERSION`** (or keep a checked-in `kernelRepo.json` from the full monorepo). Prefer connecting Vercel to the **repository root** with “Root Directory” = `landing` so parent files remain available to `write-kernel-metadata.mjs`.

---

## 4. SEO: root `robots.txt` vs Next `robots.ts`

| Artifact | Serves |
|----------|--------|
| Repository root [`robots.txt`](../../robots.txt) | Static hosts that copy the file to site root (kernel docs, static mirrors). |
| [`landing/src/app/robots.ts`](../../landing/src/app/robots.ts) | Next.js App Router → `/robots.txt` on the **deployed** landing (plus `sitemap`, `host`). |

**Policy:** The set of **training-oriented crawlers** blocked (`Disallow: /`) must stay aligned. **`npm run check-robots`** (used in Landing CI) compares root `robots.txt` with `robots.ts` and fails on mismatch.

**Disjoint hosts:** It is normal for the **kernel** static tips (e.g. `ai.txt` at repo root) and the **Next** `public/ai.txt` to be served from different origins until you unify hosting; document your deployment choice in operator notes.

---

## 5. Dashboard: iframe vs standalone

| Surface | What it is |
|---------|------------|
| **[`landing/public/dashboard.html`](../../landing/public/dashboard.html)** | Standalone interactive page (pinned React 18 UMD + Babel; see [SECURITY.md](../../SECURITY.md) / SRI). |
| **[`landing/src/app/demo/page.tsx`](../../landing/src/app/demo/page.tsx)** | Same-origin **iframe** `src="/dashboard.html"` for embedded demo UX. |

They are **the same asset**; the iframe is not a different implementation. CSP / frame rules are documented in [`landing/src/middleware.ts`](../../landing/src/middleware.ts) (`frame-src` allows same-origin dashboard).

---

## 6. Deprecating “landing on Vercel” as a separate product

**Current posture:** Vercel (or any static host) is an **optional** deployment target for `landing/`. **Deprecating** it would be an **org decision** (DNS, campaign, cost), not a code deletion requirement.

**If you shrink scope:** You may archive the Next app and serve only static HTML from `landing/public/` or from the repo root; keep **`kernelRepo.json` / robots checks** only if a reduced site remains in-tree.

---

## 7. CI summary

| Workflow | What it validates |
|----------|-------------------|
| [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) | Python quality + tests (unchanged). |
| [`.github/workflows/landing-ci.yml`](../../.github/workflows/landing-ci.yml) | `check-robots`, `kernelRepo.json` drift, ESLint, `next build`. |

---

*MoSex Macchina Lab — monorepo policy; align with README and CHANGELOG when changing deploy defaults.*
