import type { Metadata } from "next";
import Link from "next/link";

import { OnePagerLinesAccent } from "@/components/page-accents/OnePagerLinesAccent";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

const REPO = "https://github.com/CuevazaArt/ethical-android-mvp";
const SITE = "https://mosexmacchinalab.com";

export const metadata: Metadata = {
  title: "One-pager",
  description:
    "Single-page summary of the Ethical Android MVP for funders, partners, and press. Print or save as PDF from your browser.",
  openGraph: {
    title: "Ethical Android MVP — One-pager",
    description: "Research prototype summary for outreach and due diligence.",
  },
};

export default function OnePagerPage() {
  return (
    <article
      className="mx-auto min-h-full max-w-[48rem] px-6 py-10 text-zinc-200 print:max-w-none print:bg-white print:px-10 print:py-8 print:text-zinc-900"
      id="one-pager"
    >
      <header className="border-b border-white/15 pb-6 print:border-zinc-300">
        <div className="flex flex-col gap-3 print:hidden sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/about" className="hover:text-white">
                Who we are
              </Link>
              <Link href="/demo" className="hover:text-white">
                Live demo
              </Link>
              <Link href="/donate" className="hover:text-white">
                Donate
              </Link>
              <Link href="/" className="text-violet-400/90 hover:text-violet-300">
                ← Home
              </Link>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
        <p className="mt-6 text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90 print:mt-4 print:text-violet-800">
          MosEx Macchina Lab
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white print:text-zinc-950 md:text-3xl">
          Ethical Android — MVP (research prototype)
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-zinc-400 print:text-zinc-700">
          Artificial ethical consciousness, validated in simulation. Open
          source (Apache-2.0); not a commercial safety or clinical product.
        </p>
        <OnePagerLinesAccent />
      </header>

      <section className="mt-8">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500 print:text-zinc-600">
          Elevator summary
        </h2>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-300 print:text-zinc-800">
          <li>
            A <strong className="font-medium text-zinc-200 print:text-zinc-900">behavioral</strong>{" "}
            prototype: multipolar ethical evaluation, Bayesian-style belief
            updates, narrative memory, and modules that humanize limits
            (weakness pole, forgiveness decay, persistence / “soul” backup
            metaphors) — implemented in Python with formal property tests.
          </li>
          <li>
            An optional natural-language layer communicates and narrates without
            replacing kernel decisions; simulations and a browser dashboard make
            the model explorable without hardware.
          </li>
          <li>
            Goal: transparent, inspectable research in computational ethics —
            useful for discourse, teaching, and staged collaboration — not a
            substitute for regulation, clinical judgment, or legal advice.
          </li>
        </ul>
      </section>

      <section className="mt-8">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500 print:text-zinc-600">
          Due diligence & artifacts
        </h2>
        <dl className="mt-3 space-y-2 text-sm text-zinc-300 print:text-zinc-800">
          <div className="flex flex-col gap-0.5 sm:flex-row sm:gap-3">
            <dt className="shrink-0 font-medium text-zinc-400 print:text-zinc-600">
              Live site
            </dt>
            <dd>
              <a
                className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={SITE}
              >
                {SITE}
              </a>
            </dd>
          </div>
          <div className="flex flex-col gap-0.5 sm:flex-row sm:gap-3">
            <dt className="shrink-0 font-medium text-zinc-400 print:text-zinc-600">
              Interactive demo
            </dt>
            <dd>
              <a
                className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={`${SITE}/demo`}
              >
                {SITE}/demo
              </a>
            </dd>
          </div>
          <div className="flex flex-col gap-0.5 sm:flex-row sm:gap-3">
            <dt className="shrink-0 font-medium text-zinc-400 print:text-zinc-600">
              Source & license
            </dt>
            <dd>
              <a
                className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={REPO}
              >
                {REPO}
              </a>{" "}
              (Apache-2.0)
            </dd>
          </div>
          <div className="flex flex-col gap-0.5 sm:flex-row sm:gap-3">
            <dt className="shrink-0 font-medium text-zinc-400 print:text-zinc-600">
              Bibliography
            </dt>
            <dd className="break-all">
              <a
                className="text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={`${REPO}/blob/main/BIBLIOGRAPHY.md`}
              >
                {REPO}/blob/main/BIBLIOGRAPHY.md
              </a>
            </dd>
          </div>
          <div className="flex flex-col gap-0.5 sm:flex-row sm:gap-3">
            <dt className="shrink-0 font-medium text-zinc-400 print:text-zinc-600">
              Changelog / security
            </dt>
            <dd className="break-all text-zinc-400 print:text-zinc-700">
              <a
                className="text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={`${REPO}/blob/main/CHANGELOG.md`}
              >
                CHANGELOG.md
              </a>
              {" · "}
              <a
                className="text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
                href={`${REPO}/blob/main/SECURITY.md`}
              >
                SECURITY.md
              </a>
            </dd>
          </div>
        </dl>
      </section>

      <section className="mt-8">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500 print:text-zinc-600">
          Contact (no public email)
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-zinc-300 print:text-zinc-800">
          Structured first contact reduces spam. Use GitHub Issues with the
          appropriate template:
        </p>
        <ul className="mt-2 list-disc space-y-1.5 pl-5 text-sm text-zinc-300 print:text-zinc-800">
          <li>
            <a
              className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
              href={`${REPO}/issues/new?template=collaboration.yml`}
            >
              Funding, partnership, or press
            </a>
          </li>
          <li>
            <a
              className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
              href={`${REPO}/issues/new?template=question.yml`}
            >
              Technical or research question
            </a>
          </li>
          <li>
            <a
              className="break-all text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
              href={`${REPO}/issues/new?template=bug_report.yml`}
            >
              Bug report
            </a>
          </li>
          <li>
            Security: see{" "}
            <a
              className="text-violet-400/90 underline decoration-violet-400/40 underline-offset-2 print:text-violet-900"
              href={`${REPO}/blob/main/SECURITY.md`}
            >
              SECURITY.md
            </a>{" "}
            (private advisories on GitHub when enabled).
          </li>
        </ul>
      </section>

      <section className="mt-8 rounded-lg border border-white/10 bg-white/[0.02] p-4 print:border-zinc-300 print:bg-zinc-50">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500 print:text-zinc-600">
          Limitation
        </h2>
        <p className="mt-2 text-xs leading-relaxed text-zinc-500 print:text-zinc-700">
          This is a research and educational prototype. It is not certified for
          safety-critical, clinical, legal, or compliance use. Do not rely on
          it as a substitute for human judgment, institutional review, or
          domain expertise.
        </p>
      </section>

      <footer className="mt-10 border-t border-white/10 pt-6 text-xs text-zinc-500 print:border-zinc-300 print:text-zinc-600">
        <p>
          MosEx Macchina Lab · Ethical Android MVP · April 2026
        </p>
        <p className="mt-1 print:hidden">
          Tip: use your browser&apos;s <strong className="text-zinc-400">Print</strong>{" "}
          → <strong className="text-zinc-400">Save as PDF</strong> to share this
          page offline.
        </p>
      </footer>
    </article>
  );
}
