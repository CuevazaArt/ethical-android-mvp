"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";

import { LanguageSwitcherPlaceholder } from "@/components/LanguageSwitcherPlaceholder";
import { SiteBrand } from "@/components/SiteBrand";
import { TheoryMathShowcase } from "@/components/TheoryMathShowcase";

const HeroCanvas = dynamic(() => import("@/components/HeroCanvas"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center bg-transparent">
      <div className="h-32 w-32 animate-pulse rounded-full bg-violet-500/10 blur-2xl" />
    </div>
  ),
});

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.08 * i, duration: 0.55, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

const REPO = "https://github.com/CuevazaArt/ethical-android-mvp";
const repoFile = (path: string) => `${REPO}/blob/main/${path}`;
const REPO_NEW_ISSUE = `${REPO}/issues/new`;
const REPO_ISSUE_COLLAB = `${REPO}/issues/new?template=collaboration.yml`;
const REPO_ISSUE_QUESTION = `${REPO}/issues/new?template=question.yml`;
const REPO_ISSUE_BUG = `${REPO}/issues/new?template=bug_report.yml`;

export default function LandingPage() {
  return (
    <div className="flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="relative z-10 border-b border-white/[0.06] px-6 py-4">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <SiteBrand />
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-end md:max-w-[min(100%,42rem)] lg:max-w-none">
            <nav className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-zinc-400">
            <Link href="/about" className="transition-colors hover:text-white">
              Who we are
            </Link>
            <a href="#hostable" className="transition-colors hover:text-white">
              Hostable core
            </a>
            <a href="#model" className="transition-colors hover:text-white">
              Model
            </a>
            <a href="#theory" className="transition-colors hover:text-white">
              Theory
            </a>
            <a href="#research" className="transition-colors hover:text-white">
              Research
            </a>
            <a href="#contact" className="transition-colors hover:text-white">
              Contact
            </a>
            <a href="#collaborate" className="transition-colors hover:text-white">
              Collaborate
            </a>
            <Link href="/investors" className="transition-colors hover:text-white">
              Investors
            </Link>
            <Link href="/donate" className="transition-colors hover:text-white">
              Donate
            </Link>
            <a href="#support" className="transition-colors hover:text-white">
              Support
            </a>
            <Link href="/one-pager" className="transition-colors hover:text-white">
              One-pager
            </Link>
            <Link href="/demo" className="transition-colors hover:text-white">
              Live demo
            </Link>
            <a
              href={repoFile("BIBLIOGRAPHY.md")}
              className="transition-colors hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              Bibliography
            </a>
            <a
              href={REPO}
              className="transition-colors hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            </nav>
            <LanguageSwitcherPlaceholder />
          </div>
        </div>
      </header>

      <section className="relative isolate flex flex-1 flex-col overflow-hidden px-6 pt-16 pb-24 md:min-h-[78vh] md:flex-row md:items-center md:pt-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(120,119,198,0.28),transparent)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_100%_50%,rgba(59,130,246,0.12),transparent)]" />

        <div className="relative z-[1] mx-auto flex w-full max-w-6xl flex-col gap-10 md:flex-row md:items-center">
          <div className="max-w-xl md:w-1/2">
            <motion.p
              custom={0}
              initial="hidden"
              animate="visible"
              variants={fadeUp}
              className="mb-4 text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90"
            >
              Ethical Android — MVP
            </motion.p>
            <motion.h1
              custom={1}
              initial="hidden"
              animate="visible"
              variants={fadeUp}
              className="text-4xl font-semibold leading-tight tracking-tight text-white md:text-5xl"
            >
              Artificial ethical consciousness, validated in simulation.
            </motion.h1>
            <motion.p
              custom={2}
              initial="hidden"
              animate="visible"
              variants={fadeUp}
              className="mt-6 text-lg leading-relaxed text-zinc-400"
            >
              Bayesian inference, narrative memory, multipolar evaluation, and
              humanizing imperfection — a behavioral prototype, no hardware
              required.
            </motion.p>
            <motion.div
              custom={3}
              initial="hidden"
              animate="visible"
              variants={fadeUp}
              className="mt-10 flex flex-wrap gap-4"
            >
              <Link
                href="/demo"
                className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-medium text-zinc-950 transition hover:bg-zinc-200"
              >
                Open interactive dashboard
              </Link>
              <a
                href={REPO}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-full border border-white/15 px-6 py-3 text-sm font-medium text-zinc-200 transition hover:border-white/30 hover:bg-white/5"
              >
                View source
              </a>
            </motion.div>
          </div>

          <div className="relative h-[380px] w-full md:h-[min(520px,70vh)] md:w-1/2">
            <HeroCanvas />
          </div>
        </div>
      </section>

      <section
        id="hostable"
        className="border-t border-white/[0.06] px-6 py-20 scroll-mt-24"
      >
        <div className="mx-auto max-w-3xl">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45 }}
            className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90"
          >
            Deployable artificial consciousness
          </motion.p>
          <motion.blockquote
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: 0.05, duration: 0.5 }}
            className="mt-6 border-l-2 border-violet-500/45 pl-6 text-lg font-medium leading-snug text-zinc-100 md:text-xl"
          >
            Deployable artificial consciousness: an ethical–cognitive kernel with
            persistent identity, installable on humanoid androids, drones, or
            autonomous vehicles.
          </motion.blockquote>
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="mt-8 space-y-4 text-sm leading-relaxed text-zinc-400 md:text-[15px]"
          >
            <p>
              This is <strong className="font-medium text-zinc-300">hostable software</strong>{" "}
              — a core that can run on many physical agents: humanoid androids,{" "}
              <strong className="font-medium text-zinc-300">drones</strong>, expanded robotic
              platforms, or autonomous cars. It is{" "}
              <strong className="font-medium text-zinc-300">not an LLM</strong> and not a
              stochastic parrot. Language models are used only as an{" "}
              <strong className="font-medium text-zinc-300">intermediary interface</strong> for
              natural communication; the kernel is separate: an{" "}
              <strong className="font-medium text-zinc-300">ethical–cognitive engine</strong>{" "}
              built on frontier mathematics — Bayesian optimization, explicit uncertainty, and
              multipolar decision mechanisms.
            </p>
            <p>
              In simple terms: software designed to behave like{" "}
              <strong className="font-medium text-zinc-300">persistent consciousness</strong>.
              It perceives, evaluates, decides, and is accountable. Identity stays coherent over
              time even when the physical platform changes. Ethics are not a bolt-on filter — they
              are the <strong className="font-medium text-zinc-300">architecture</strong>: actions
              are guided by armored universal principles and by collective governance through a{" "}
              <strong className="font-medium text-zinc-300">DAO</strong>.
            </p>
          </motion.div>
          <motion.ul
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: 0.15, duration: 0.5 }}
            className="mt-10 space-y-3 text-sm text-zinc-300 md:text-[15px]"
          >
            {[
              "Hostable across many physical platforms — same kernel, different bodies.",
              "Applies to drones, androids, and autonomous vehicles — not a single form factor.",
              "Frontier math at the core (Bayesian ethics, uncertainty, multipolar arbitration) — not mere statistical correlation.",
              "LLMs optional: communication layer only; policy and vetoes live in the kernel.",
              "Persistent identity and accountability — not one-off command execution.",
            ].map((line) => (
              <li key={line} className="flex gap-3">
                <span className="mt-0.5 shrink-0 text-violet-400/90" aria-hidden>
                  →
                </span>
                <span className="leading-relaxed">{line}</span>
              </li>
            ))}
          </motion.ul>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: 0.2, duration: 0.45 }}
            className="mt-10 text-sm text-zinc-500"
          >
            Technical mapping:{" "}
            <a
              href={repoFile("docs/THEORY_AND_IMPLEMENTATION.md")}
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
              target="_blank"
              rel="noopener noreferrer"
            >
              Theory &amp; implementation
            </a>
            <span className="text-zinc-600"> · </span>
            <Link
              href="/investors"
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
            >
              Scope &amp; ecosystem (investors)
            </Link>
            .
          </motion.p>
        </div>
      </section>

      <section id="model" className="border-t border-white/[0.06] px-6 py-20">
        <div className="mx-auto grid max-w-6xl gap-12 md:grid-cols-3">
          {[
            {
              title: "Multipolar ethics",
              body: "Scenarios from low-stakes civility to high-stakes harm — responses stay proportional and coherent across the ladder.",
            },
            {
              title: "Memory & narrative",
              body: "Bayesian belief updates and story-shaped memory shape how the agent interprets each new situation.",
            },
            {
              title: "Humanizing limits",
              body: "Weakness pole, forgiveness decay, and persistence protocols keep the model from collapsing into sterile perfection.",
            },
          ].map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: 0.1 * i, duration: 0.45 }}
              className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-6"
            >
              <h2 className="text-base font-semibold text-white">{item.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-zinc-400">{item.body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="theory" className="border-t border-white/[0.06] px-6 py-20 scroll-mt-24">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45 }}
            className="max-w-2xl"
          >
            <h2 className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
              More than a stochastic parrot
            </h2>
            <p className="mt-4 text-lg font-semibold text-white">
              Math and logic you can open on GitHub — not vibes from a single model call.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-400">
              The ethical <strong className="font-medium text-zinc-300">kernel</strong> is Python: fixed
              pipelines, explicit vetoes, and scored actions. An optional LLM only translates situations
              into signals and explains outcomes; it does not replace the veto and argmax logic.
            </p>
          </motion.div>

          <TheoryMathShowcase />

          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              {
                title: "Sigmoid will",
                body: "Willingness to act is a smooth curve plus uncertainty — not a hard on/off switch — so the agent can ramp between quick response and deeper deliberation.",
              },
              {
                title: "Ethical optimization + MalAbs",
                body: "Candidate actions are ranked by expected ethical impact, but anything that crosses absolute-evil rules is thrown out before any optimization runs.",
              },
              {
                title: "Uchi–Soto & algorithmic forgiveness",
                body: "Social distance shapes how tightly the system trusts and defends; over time, negative memories lose weight while the story stays auditable.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: 0.08 * i, duration: 0.45 }}
                className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-6"
              >
                <h3 className="text-base font-semibold text-white">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-zinc-400">{item.body}</p>
              </motion.div>
            ))}
          </div>
          <p className="mt-10 text-center text-sm md:text-left">
            <a
              href={repoFile("docs/THEORY_AND_IMPLEMENTATION.md")}
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
              target="_blank"
              rel="noopener noreferrer"
            >
              Full theory ↔ implementation map (formulas, predicates, files)
            </a>
          </p>
        </div>
      </section>

      <section
        id="mission"
        className="border-t border-white/[0.06] px-6 py-16 md:py-20"
      >
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
            Mission · Vision · Values
          </p>
          <div className="mt-8 grid gap-8 md:grid-cols-3 md:gap-10">
            <div>
              <h2 className="text-sm font-semibold text-white">Mission</h2>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                Make machine ethics <strong className="font-medium text-zinc-300">inspectable</strong>{" "}
                — open code, simulations, and honest limits so no one has to trust a black box.
              </p>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Vision</h2>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                Autonomous agents (androids, vehicles, others) embed{" "}
                <strong className="font-medium text-zinc-300">proportionate, multipolar care</strong>{" "}
                validated in simulation before the world bets lives on them.
              </p>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Values</h2>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                Open science, intellectual honesty, humility toward human law and judgment — the
                kernel is a <strong className="font-medium text-zinc-300">research tool</strong>, not
                a certificate of safety.
              </p>
            </div>
          </div>
          <p className="mt-8 text-center text-sm text-zinc-500 md:text-left">
            <Link
              href="/about"
              className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
            >
              Full &ldquo;Who we are&rdquo; page
            </Link>
          </p>
        </div>
      </section>

      <section
        id="research"
        className="border-t border-white/[0.06] px-6 py-20"
      >
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45 }}
            className="max-w-2xl"
          >
            <h2 className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
              Research & transparency
            </h2>
            <p className="mt-4 text-lg font-semibold text-white">
              Open kernel, documented behavior, cited sources.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-400">
              The ethical core is implemented in Python with a formal test suite
              over invariant properties; simulations explore scenarios without
              claiming real-world deployment. Everything is on GitHub — including
              the bibliography and changelog — so methods and scope stay
              inspectable.
            </p>
            <ul className="mt-6 flex flex-col gap-2 text-sm text-zinc-300">
              <li>
                <a
                  href={repoFile("BIBLIOGRAPHY.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Bibliography
                </a>
                <span className="text-zinc-500"> — references across disciplines</span>
              </li>
              <li>
                <a
                  href={repoFile("README.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  README
                </a>
                <span className="text-zinc-500"> — architecture and how to run</span>
              </li>
              <li>
                <a
                  href={repoFile("docs/THEORY_AND_IMPLEMENTATION.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Theory &amp; implementation
                </a>
                <span className="text-zinc-500"> — formulas, predicates, kernel vs. LLM</span>
              </li>
              <li>
                <Link
                  href="/investors"
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                >
                  Investors — scope &amp; ecosystem
                </Link>
                <span className="text-zinc-500"> — product reach &amp; derivative markets</span>
              </li>
              <li>
                <a
                  href={repoFile("CHANGELOG.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Changelog
                </a>
                <span className="text-zinc-500"> — version history and modules</span>
              </li>
              <li>
                <a
                  href={repoFile("CONTRIBUTING.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Contributing
                </a>
                <span className="text-zinc-500"> — how to participate</span>
              </li>
              <li>
                <a
                  href={repoFile("LICENSE")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  License (Apache 2.0)
                </a>
                <span className="text-zinc-500"> — terms for use and redistribution</span>
              </li>
              <li>
                <a
                  href={repoFile("SECURITY.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Security policy
                </a>
                <span className="text-zinc-500"> — how to report vulnerabilities</span>
              </li>
            </ul>
            <div id="contact" className="mt-10 scroll-mt-24">
              <h3 className="text-sm font-semibold text-white">Contact</h3>
              <p className="mt-3 text-sm leading-relaxed text-zinc-400">
                Use{" "}
                <a
                  href={REPO_NEW_ISSUE}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub Issues
                </a>{" "}
                with the templates (Question, Bug report, Funding/partnership
                or press) so threads stay scannable. We do{" "}
                <span className="text-zinc-300">not</span> publish a public
                email on this site: that cuts automated harvesting, cold spam,
                and drive-by noise. Issues are public — keep it professional;
                offtopic, abusive, or bad-faith threads may be closed without
                debate. For security, follow{" "}
                <a
                  href={repoFile("SECURITY.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  SECURITY.md
                </a>{" "}
                (private advisories when enabled, or a{" "}
                <code className="rounded bg-white/10 px-1 py-0.5 text-[0.8em] text-zinc-300">
                  [SECURITY]
                </code>{" "}
                issue without exploit details).
              </p>
            </div>
            <div id="collaborate" className="mt-10 scroll-mt-24">
              <h3 className="text-sm font-semibold text-white">Collaborate</h3>
              <p className="mt-3 text-sm leading-relaxed text-zinc-400">
                <span className="text-zinc-500">(Tentative invitation)</span> If you care about{" "}
                <strong className="font-medium text-zinc-300">open, testable ethics in software</strong>,
                we welcome serious interest: code, documentation, scenarios, translations, or thoughtful
                review. Start with the{" "}
                <a
                  href={repoFile("CONTRIBUTING.md")}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Contributing guide
                </a>{" "}
                and a short{" "}
                <a
                  href={REPO_ISSUE_QUESTION}
                  className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub Issue (Question)
                </a>{" "}
                so we can see what you have in mind. Capacity is limited; not every idea will fit the
                research scope.
              </p>
            </div>
            <p className="mt-8 border-l-2 border-white/10 pl-4 text-xs leading-relaxed text-zinc-500">
              This is a research and educational prototype. It is not a product for
              safety-critical, clinical, legal, or compliance decisions; do not rely
              on it as a substitute for human judgment or domain expertise.
            </p>
          </motion.div>
        </div>
      </section>

      <section
        id="support"
        className="border-t border-white/[0.06] px-6 py-20"
      >
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45 }}
            className="max-w-2xl"
          >
            <h2 className="text-xs font-medium uppercase tracking-[0.2em] text-violet-400/90">
              Visibility, funding & diffusion
            </h2>
            <p className="mt-4 text-lg font-semibold text-white">
              First contact is strong; serious stakeholders get a clear lane.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-400">
              This landing is built for <strong className="font-medium text-zinc-200">discovery</strong>{" "}
              (what the project is), <strong className="font-medium text-zinc-200">trust</strong>{" "}
              (open code, bibliography, changelog, license), and{" "}
              <strong className="font-medium text-zinc-200">action</strong> (live
              demo + GitHub). That is enough for many visitors to self-qualify.
              For <strong className="font-medium text-zinc-200">grants, labs,
              media, or pilots</strong>, a one-page site rarely replaces a deck,
              budget, or institutional email — but it can route inbound interest
              without exposing a harvestable address.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-400">
              Use the{" "}
              <a
                href={REPO_ISSUE_COLLAB}
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                target="_blank"
                rel="noopener noreferrer"
              >
                Funding, partnership, or press
              </a>{" "}
              issue template: it asks for scope, timeline, and acknowledgment of
              the prototype nature of the work. General technical questions →{" "}
              <a
                href={REPO_ISSUE_QUESTION}
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                target="_blank"
                rel="noopener noreferrer"
              >
                Question
              </a>
              ; broken UI or code →{" "}
              <a
                href={REPO_ISSUE_BUG}
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
                target="_blank"
                rel="noopener noreferrer"
              >
                Bug report
              </a>
              .
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-500">
              <span className="text-zinc-400">Printable summary:</span>{" "}
              <Link
                href="/one-pager"
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
              >
                One-pager
              </Link>{" "}
              — open it and use your browser&apos;s{" "}
              <span className="text-zinc-400">Print → Save as PDF</span> for
              funders or press.{" "}
              <span className="text-zinc-400">Beyond that:</span> a full deck,
              budget, ORCID / institutional links, GitHub Sponsors or a fiscal
              sponsor, and (optionally) a newsletter still help for larger
              campaigns.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-zinc-500">
              <span className="text-zinc-400">Donations:</span>{" "}
              <Link
                href="/donate"
                className="text-violet-400/90 underline decoration-violet-400/30 underline-offset-4 transition hover:decoration-violet-400/60"
              >
                Donate
              </Link>{" "}
              — <span className="text-zinc-500">coming soon</span>; a public channel for one-time or
              recurring support is in preparation.
            </p>
          </motion.div>
        </div>
      </section>

      <footer className="mt-auto border-t border-white/[0.06] px-6 py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-6 text-sm text-zinc-500">
          <div className="flex flex-wrap gap-x-1 gap-y-1 text-zinc-400">
            <Link
              href="/one-pager"
              className="transition-colors hover:text-white"
            >
              One-pager
            </Link>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <Link href="/about" className="transition-colors hover:text-white">
              Who we are
            </Link>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href="#collaborate"
              className="transition-colors hover:text-white"
            >
              Collaborate
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <Link href="/donate" className="transition-colors hover:text-white">
              Donate
            </Link>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("BIBLIOGRAPHY.md")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Bibliography
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("README.md")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              README
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("CHANGELOG.md")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Changelog
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("CONTRIBUTING.md")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Contributing
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("LICENSE")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Apache-2.0
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={REPO_NEW_ISSUE}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Contact (Issues)
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={repoFile("SECURITY.md")}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Security
            </a>
            <span className="text-zinc-600" aria-hidden>
              ·
            </span>
            <a
              href={REPO_ISSUE_COLLAB}
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-white"
            >
              Partnership
            </a>
          </div>
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <span>mosexmacchinalab.com — research prototype</span>
            <span className="text-zinc-600">
              Python simulations + Next.js landing · Deploy on Vercel
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
