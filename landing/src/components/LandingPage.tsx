"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";

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

export default function LandingPage() {
  return (
    <div className="flex min-h-full flex-col bg-[#050508] text-zinc-100">
      <header className="relative z-10 border-b border-white/[0.06] px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <span className="text-sm font-medium tracking-tight text-zinc-300">
            Mosex Macchina Lab
          </span>
          <nav className="flex gap-6 text-sm text-zinc-400">
            <a href="#model" className="transition-colors hover:text-white">
              Model
            </a>
            <Link href="/demo" className="transition-colors hover:text-white">
              Live demo
            </Link>
            <a
              href="https://github.com/CuevazaArt/ethical-android-mvp"
              className="transition-colors hover:text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </nav>
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
                href="https://github.com/CuevazaArt/ethical-android-mvp"
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

      <footer className="mt-auto border-t border-white/[0.06] px-6 py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 text-sm text-zinc-500 md:flex-row md:items-center md:justify-between">
          <span>mosexmacchinalab.com — research prototype</span>
          <span className="text-zinc-600">
            Python simulations + Next.js landing · Deploy on Vercel
          </span>
        </div>
      </footer>
    </div>
  );
}
