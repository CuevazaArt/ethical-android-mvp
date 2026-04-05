import type { Metadata } from "next";
import Link from "next/link";

import { AboutPeopleAccent } from "@/components/page-accents/AboutPeopleAccent";
import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";

export const metadata: Metadata = {
  title: "Who we are",
  description:
    "MosEx Macchina Lab — mission, vision, and values behind the Ethical Android research prototype.",
};

export default function AboutPage() {
  return (
    <div className="relative flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="shrink-0 border-b border-white/[0.08] px-4 py-3 md:px-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <SiteBrand />
          <div className="flex flex-wrap items-center gap-3 sm:justify-end">
            <nav className="flex flex-wrap gap-4 text-sm text-zinc-400">
              <Link href="/" className="hover:text-white">
                Home
              </Link>
              <Link href="/demo" className="hover:text-white">
                Live demo
              </Link>
              <Link href="/donate" className="hover:text-white">
                Donate
              </Link>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <AboutPeopleAccent />

      <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-12 md:py-16">
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
          MosEx Macchina Lab
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Who we are
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-zinc-400">
          We are a small research-oriented group building an{" "}
          <strong className="font-medium text-zinc-300">open, inspectable</strong> prototype of
          ethical decision-making for autonomous agents — not a product company and not a
          certification body. The Ethical Android MVP is our public simulation kernel: code,
          tests, bibliography, and demos anyone can audit.
        </p>

        <section className="mt-12 border-t border-white/[0.08] pt-10">
          <h2 className="text-lg font-semibold text-white">Mission</h2>
          <p className="mt-3 text-sm leading-relaxed text-zinc-400">
            Advance <strong className="font-medium text-zinc-300">transparent machine ethics</strong>{" "}
            through documented models, formal checks, and honest limits — so stakeholders can see{" "}
            <em>how</em> a system weighs harm, care, and uncertainty before anyone asks them to trust
            it blindly.
          </p>
        </section>

        <section className="mt-10">
          <h2 className="text-lg font-semibold text-white">Vision</h2>
          <p className="mt-3 text-sm leading-relaxed text-zinc-400">
            Autonomous systems — from assistive androids to vehicles and other agents — embed{" "}
            <strong className="font-medium text-zinc-300">multipolar, proportionate reasoning</strong>{" "}
            that respects life and dignity, admits imperfection, and stays open to critique and law —
            with behavior validated in simulation long before high-stakes deployment.
          </p>
        </section>

        <section className="mt-10">
          <h2 className="text-lg font-semibold text-white">Values</h2>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-relaxed text-zinc-400">
            <li>
              <strong className="font-medium text-zinc-300">Open science</strong> — source, tests,
              and citations on the table.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Intellectual honesty</strong> — we label
              the MVP as research, not a safety guarantee.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Proportionality & care</strong> — stakes
              and vulnerability shape how hard the model pushes back.
            </li>
            <li>
              <strong className="font-medium text-zinc-300">Humility</strong> — human judgment and
              institutions stay in charge; the kernel is a tool for discourse and design.
            </li>
          </ul>
        </section>

        <p className="mt-12 text-xs text-zinc-600">
          <Link
            href="/"
            className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 hover:decoration-violet-400/60"
          >
            ← Back to the landing page
          </Link>
        </p>
      </main>
    </div>
  );
}
