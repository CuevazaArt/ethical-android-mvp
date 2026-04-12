## Ethos Kernel — public landing (Next.js)

**Monorepo role:** Optional **marketing / education** site for the Python kernel in the repository root. It is **officially supported** in-tree but **not** part of the kernel runtime. Full policy: [`docs/proposals/LANDING_DECOUPLING_AND_SUPPORT.md`](../docs/proposals/LANDING_DECOUPLING_AND_SUPPORT.md).

**Version sync:** After changing `../pyproject.toml` or this package’s `version`, run `npm run sync-kernel-meta` and commit `src/config/kernelRepo.json`. CI enforces no drift.

**Robots / training crawlers:** Root `../robots.txt` must stay aligned with `src/app/robots.ts`; run `npm run check-robots`.

This project was bootstrapped with [Next.js](https://nextjs.org) [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting started

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Crawling, SEO, and AI corpus signals

This section records the **deliberate trade-off** between discoverability (campaign indexing) and signals to crawlers used for model training.

| Topic | Location |
|-------|----------|
| **SEO / search engines** | `src/app/robots.ts`: `User-agent: *` → `allow: /` + `sitemap`. The landing may be indexed normally. |
| **Training-oriented crawlers** | Same rules: `disallow: /` for listed user-agents (e.g. GPTBot, Google-Extended, CCBot). This is a **signal**, not a substitute for a private repo or contractual agreements. |
| **Declared preference (non-contractual)** | `public/ai.txt` in deployment (`/ai.txt`). |

Strong protection for source code still relies on a **private repository**, access control, and agreements (NDA) during due diligence—not `robots.txt` alone.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a font family for Vercel.

## Learn more

- [Next.js Documentation](https://nextjs.org/docs) — Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) — interactive tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js); feedback and contributions are welcome.

## Deploy on Vercel

The usual path is the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

See the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for details.
