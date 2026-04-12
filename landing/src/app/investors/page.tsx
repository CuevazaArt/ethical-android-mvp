import type { Metadata } from "next";
import Link from "next/link";

import { InvestorsGrowthAccent } from "@/components/page-accents/InvestorsGrowthAccent";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

const REPO = "https://github.com/CuevazaArt/ethical-android-mvp";
const THEORY = `${REPO}/blob/main/docs/proposals/THEORY_AND_IMPLEMENTATION.md`;

export const metadata: Metadata = {
  title: "Investors — scope & ecosystem",
  description:
    "Hypothetical reach if a production stack existed: research kernel v0.0.0 today (Git only, no PyPI, no external benchmark; DAO mock).",
  robots: { index: true, follow: true },
};

const MAIN_SCOPE = [
  {
    title: "Toys with persistent, configurable identity",
    body: "Companions that grow with the user and adapt to their development.",
  },
  {
    title: "Playful agents with identity",
    body: "They entertain, teach, and offer emotional support — not disposable scripts.",
  },
  {
    title: "Anthropomorphic or human-like androids",
    body: "Built to earn emotional attachment and long-term trust.",
  },
  {
    title: "Task-specific or general-purpose services",
    body: "Agents tuned for narrow missions or broad everyday use.",
  },
  {
    title: "Industrial arms & manufacturing robots",
    body: "Productive automation with coherent identity and ethical continuity on the floor.",
  },
  {
    title: "Service consoles & front-line interfaces",
    body: "Reliable touchpoints for care, support, and public-facing operations.",
  },
  {
    title: "Autonomous driving & safe navigation",
    body: "Vehicles guided by explicit ethical criteria, not opaque reward hacks alone.",
  },
  {
    title: "Ethical oversight devices",
    body: "Monitoring with human-aligned values and preloaded principles — not bare maximization.",
  },
  {
    title: "Advanced smart-home / domotics",
    body: "Natural-language interaction with a kernel that can explain and justify behavior.",
  },
  {
    title: "Multilingual interfaces",
    body: "Fluid communication across most major languages without swapping the ethical core.",
  },
] as const;

const VALUE_PROPS = [
  {
    title: "Ethical trust",
    body: "Strong moral compass, foundational values, and hard vetoes against absolute harm.",
  },
  {
    title: "Emotional companionship",
    body: "Designed for attachment and a sense of belonging — responsibly bounded.",
  },
  {
    title: "Identity continuity",
    body: "Persistence protocols (including immortality-style backup narratives in the research stack) so the self does not reset with every hardware swap.",
  },
  {
    title: "Narrative adaptability",
    body: "Behavior tracks the user’s context and story-shaped memory, not only the last command.",
  },
  {
    title: "Safety & everyday assistance",
    body: "Reminders, protection, and practical support grounded in the same ethical engine.",
  },
] as const;

const ECOSYSTEM = [
  {
    title: "Native DAO",
    body: "Decentralized governance for ethical legitimacy and community voice — in-repo today this is mock / simulated; on-chain would be a separate compliance and engineering program.",
  },
  {
    title: "Hardware lifecycle",
    body: "Design, upgrades, mechanical maintenance, and physical upkeep of embodied platforms.",
  },
  {
    title: "Financial services & insurance",
    body: "Financing models, identity protection, and continuity guarantees tied to persistent agents.",
  },
  {
    title: "Adjacent technologies",
    body: "Batteries, sensors, connectivity stacks — everything the body needs to run the kernel.",
  },
  {
    title: "Social & legal framing",
    body: "Law, policy, education, and public understanding as the ecosystem matures.",
  },
  {
    title: "Civil regulation & public safety",
    body: "Norms for coexistence, incident response, and accountable deployment in shared space.",
  },
  {
    title: "Ecological policy",
    body: "Sustainable development and environmental responsibility at fleet and product level.",
  },
] as const;

export default function InvestorsPage() {
  return (
    <div className="relative flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-6">
        <div className="mx-auto flex max-w-4xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/" className="transition-colors hover:text-white">
                Home
              </Link>
              <Link href="/#hostable" className="transition-colors hover:text-white">
                Hostable core
              </Link>
              <Link href="/demo" className="transition-colors hover:text-white">
                Live demo
              </Link>
              <Link href="/one-pager" className="transition-colors hover:text-white">
                One-pager
              </Link>
              <Link href="/roadmap" className="transition-colors hover:text-white">
                Roadmap
              </Link>
              <Link href="/blockchain-dao" className="transition-colors hover:text-white">
                BlockChainDAO
              </Link>
              <Link href="/donate" className="transition-colors hover:text-white">
                Donate
              </Link>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <InvestorsGrowthAccent />

      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto w-full max-w-4xl flex-1 px-6 py-12 outline-none focus-visible:ring-2 focus-visible:ring-violet-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#050508] md:py-16"
      >
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
          For investors &amp; partners
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Scope &amp; ecosystem — hypothetical product surfaces
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-400 md:text-[15px]">
          This page sketches{" "}
          <strong className="font-medium text-zinc-300">where a mature ethical kernel could matter</strong>{" "}
          if brought to production — not what ships today. The Ethos Kernel is{" "}
          <strong className="font-medium text-zinc-300">v0.0.0</strong>, installable from Git only
          (not PyPI), validated by internal invariant tests rather than an independent external
          benchmark, with <strong className="font-medium text-zinc-300">mock</strong> DAO hooks. The
          categories below are directional for due diligence, not a product roadmap promise.
        </p>
        <p className="mt-4 text-sm text-zinc-500">
          For{" "}
          <strong className="font-medium text-zinc-400">what is already built</strong>,{" "}
          <strong className="font-medium text-zinc-400">planned engineering</strong>, and{" "}
          <strong className="font-medium text-zinc-400">funding or collaboration asks</strong>, see
          the{" "}
          <Link
            href="/roadmap"
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
          >
            roadmap &amp; collaboration
          </Link>{" "}
          page.
        </p>

        <section className="mt-14 border-t border-white/[0.08] pt-12">
          <h2 className="text-lg font-semibold text-white md:text-xl">
            Illustrative product scope
          </h2>
          <p className="mt-2 text-sm text-zinc-500">
            Example surfaces if a hostable ethical–cognitive kernel were productized — not current SKUs.
          </p>
          <ul className="mt-8 grid gap-4 sm:grid-cols-2">
            {MAIN_SCOPE.map((item) => (
              <li
                key={item.title}
                className="rounded-xl border border-white/[0.08] bg-white/[0.02] p-4"
              >
                <h3 className="text-sm font-semibold text-zinc-100">{item.title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-zinc-400 md:text-sm">
                  {item.body}
                </p>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-14 border-t border-white/[0.08] pt-12">
          <h2 className="text-lg font-semibold text-white md:text-xl">Value proposition</h2>
          <p className="mt-2 text-sm text-zinc-500">
            What a future product could offer beyond “smarter automation” — not a claim about a shipping SKU.
          </p>
          <ul className="mt-8 space-y-5">
            {VALUE_PROPS.map((item) => (
              <li key={item.title} className="flex gap-3 border-l-2 border-violet-500/35 pl-4">
                <div>
                  <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-zinc-400">{item.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-14 border-t border-white/[0.08] pt-12">
          <h2 className="text-lg font-semibold text-white md:text-xl">Ecosystem derivatives</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Adjacent markets and institutions that emerge around persistent, governed agents.
          </p>
          <ul className="mt-8 space-y-5">
            {ECOSYSTEM.map((item) => (
              <li key={item.title} className="flex gap-3 border-l-2 border-sky-500/30 pl-4">
                <div>
                  <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-zinc-400">{item.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-14 border-t border-white/[0.08] pt-12">
          <h2 className="text-lg font-semibold text-white md:text-xl">Conclusion</h2>
          <p className="mt-4 text-sm leading-relaxed text-zinc-400 md:text-[15px]">
            If matured, a kernel like this could address toys, industry, mobility, oversight, and
            home intelligence; the surrounding ecosystem could add governance (DAO roadmap; mock
            today), hardware services, finance and insurance, enabling technologies, and social and
            regulatory fabric. That frames a possible{" "}
            <strong className="font-medium text-zinc-300">integrated opportunity</strong> — while
            today&apos;s artifact remains open code, simulation-first, and bounded by the transparency
            notes in the repository.
          </p>
        </section>

        <p className="mt-12 text-center text-sm text-zinc-500 md:text-left">
          <Link
            href={THEORY}
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
            target="_blank"
            rel="noopener noreferrer"
          >
            Theory &amp; implementation (GitHub)
          </Link>
          <span className="mx-2 text-zinc-600">·</span>
          <Link
            href={`${REPO}/issues/new?template=collaboration.yml`}
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
            target="_blank"
            rel="noopener noreferrer"
          >
            Partnership / funding (GitHub issue)
          </Link>
        </p>
      </main>
    </div>
  );
}
