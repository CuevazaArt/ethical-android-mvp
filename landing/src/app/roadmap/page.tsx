import type { Metadata } from "next";
import Link from "next/link";

import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { RoadmapTimelineAccent } from "@/components/page-accents/RoadmapTimelineAccent";
import { SiteBrand } from "@/components/SiteBrand";

const REPO = "https://github.com/CuevazaArt/ethical-android-mvp";
const COLLAB = `${REPO}/issues/new?template=collaboration.yml`;

export const metadata: Metadata = {
  title: "Roadmap & collaboration",
  description:
    "What exists today, planned implementations, and how to fund or collaborate on the Ethical Android research prototype.",
  robots: { index: true, follow: true },
};

const CURRENT = [
  "Python ethical kernel with multipolar poles, Bayesian-style scoring, MalAbs vetoes, narrative memory, forgiveness, Ψ-sleep (simulation), and optional LLM interface layer.",
  "Formal property tests (`pytest`) and scenario runner for reproducible behavior.",
  "Public Next.js site: landing, theory math showcase, investors scope page, interactive dashboard (browser), one-pager for outreach.",
  "Documentation: README, THEORY_AND_IMPLEMENTATION, SECURITY, bibliography — Apache-2.0.",
] as const;

const NEAR_TERM = [
  "Richer test matrix: edge cases, adversarial prompts against the LLM boundary, regression suite for domain additions.",
  "Reference “sensor → signals” adapters (documented stubs or one hardware-agnostic demo path) without claiming product certification.",
  "Conversation/session state design: multi-turn loops that keep the kernel authoritative over policy.",
  "Dashboard build pipeline: pre-bundle JSX to reduce in-browser Babel reliance (security & performance).",
  "Identity & voice guardrails: structured profile the kernel owns; LLM restricted to phrasing.",
] as const;

const MID_TERM = [
  "Governance beyond mock DAO: requirements, threat model, and optional testnet-style experiments — only with legal and partner clarity.",
  "Pilot integrations with robotics or vehicle stacks in **staged, supervised** environments — never as a substitute for regulation.",
  "External ethics or safety review cycles documented in the open.",
] as const;

const NEEDS = [
  {
    title: "Sponsored engineering",
    body: "Time to implement the near-term roadmap, maintain CI, and respond to security reports — ideally scoped grants or part-time contracts.",
  },
  {
    title: "Research & ethics partners",
    body: "Universities, labs, or civil-society groups for co-authored scenarios, red-teaming, and policy-facing briefs.",
  },
  {
    title: "Hardware / integration partners",
    body: "Short spikes to map real sensors and actuators to the kernel’s signal model — no implied warranty on deployments.",
  },
  {
    title: "Operations",
    body: "Sustainable hosting, domain/DNS hygiene, and occasional legal review for disclosures and contributor agreements.",
  },
  {
    title: "Community",
    body: "Contributors for docs, translations, simulation scenarios, and reproducible bug reports.",
  },
] as const;

export default function RoadmapPage() {
  return (
    <div className="relative flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/" className="transition-colors hover:text-white">
                Home
              </Link>
              <Link href="/investors" className="transition-colors hover:text-white">
                Investors
              </Link>
              <Link href="/blockchain-dao" className="transition-colors hover:text-white">
                BlockChainDAO
              </Link>
              <Link href="/donate" className="transition-colors hover:text-white">
                Donate
              </Link>
              <Link href="/demo" className="transition-colors hover:text-white">
                Live demo
              </Link>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <RoadmapTimelineAccent />

      <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-12 md:py-16">
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
          Transparency
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Roadmap &amp; collaboration
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-zinc-400 md:text-[15px]">
          This page lives on its own so funders, partners, and contributors can
          bookmark it and see{" "}
          <strong className="font-medium text-zinc-300">what already exists</strong>,{" "}
          <strong className="font-medium text-zinc-300">what we plan to build next</strong>, and{" "}
          <strong className="font-medium text-zinc-300">what we need from others</strong> — in
          one place. It complements the{" "}
          <Link href="/investors" className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60">
            investors
          </Link>{" "}
          scope narrative without overloading that page.
        </p>

        <section className="mt-12 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Current foundation (in the repo)</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Shipped and inspectable today — not a future promise.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            {CURRENT.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="mt-10 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Near-term implementation roadmap</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Concrete technical directions — priorities may shift with funding and partners.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            {NEAR_TERM.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="mt-10 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Mid-term (aspirational)</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Depends on governance, capital, and institutional alignment — listed for honesty, not
            as commitments with dates.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            {MID_TERM.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm text-zinc-500">
            For mock vs on-chain governance narrative, see{" "}
            <Link
              href="/blockchain-dao"
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
            >
              BlockChainDAO
            </Link>
            .
          </p>
        </section>

        <section className="mt-10 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">
            Funding &amp; collaboration needs
          </h2>
          <p className="mt-2 text-sm text-zinc-500">
            Where outside help directly accelerates the roadmap.
          </p>
          <ul className="mt-6 space-y-5">
            {NEEDS.map((n) => (
              <li
                key={n.title}
                className="border-l-2 border-orange-500/35 pl-4"
              >
                <h3 className="text-sm font-semibold text-emerald-200/90">{n.title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-zinc-400">{n.body}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-12 rounded-xl border border-white/[0.08] bg-white/[0.02] p-6">
          <h2 className="text-sm font-semibold text-white">Engage</h2>
          <p className="mt-3 text-sm leading-relaxed text-zinc-400">
            Use the{" "}
            <a
              href={COLLAB}
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
              target="_blank"
              rel="noopener noreferrer"
            >
              partnership / funding GitHub template
            </a>{" "}
            for scoped proposals. For security-sensitive reports, see{" "}
            <a
              href={`${REPO}/blob/main/SECURITY.md`}
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
              target="_blank"
              rel="noopener noreferrer"
            >
              SECURITY.md
            </a>
            . Donation channels:{" "}
            <Link
              href="/donate"
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
            >
              Donate
            </Link>
            .
          </p>
        </section>

        <p className="mt-10 text-center text-xs text-zinc-600 md:text-left">
          Last updated with the repository; substantive roadmap edits should land via PR or tracked
          issue.
        </p>
      </main>
    </div>
  );
}
