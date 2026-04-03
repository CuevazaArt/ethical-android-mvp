"use client";

import { useEffect, useId, useState } from "react";

const INTRO_STORAGE_KEY = "ethical-android-mvp-demo-intro-open";

export function DemoIntroPanel() {
  const [open, setOpen] = useState(true);
  const headingId = useId();
  const panelId = useId();

  useEffect(() => {
    try {
      const raw = localStorage.getItem(INTRO_STORAGE_KEY);
      if (raw !== "false" && raw !== "true") return;
      const next = raw === "true";
      queueMicrotask(() => setOpen(next));
    } catch {
      /* private mode / quota */
    }
  }, []);

  const toggleOpen = () => {
    setOpen((prev) => {
      const next = !prev;
      try {
        localStorage.setItem(INTRO_STORAGE_KEY, next ? "true" : "false");
      } catch {
        /* ignore */
      }
      return next;
    });
  };

  return (
    <section
      className="shrink-0 border-b border-white/[0.06] bg-[#07070c]"
      aria-labelledby={headingId}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 md:px-5">
        <h1
          id={headingId}
          className="text-base font-semibold tracking-tight text-zinc-100 md:text-lg"
        >
          What you&apos;re seeing
        </h1>
        <button
          type="button"
          className="shrink-0 rounded-lg border border-violet-500/40 bg-violet-950/40 px-3 py-2 text-xs font-semibold text-violet-200 shadow-sm transition hover:border-violet-400/60 hover:bg-violet-900/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-400/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#07070c]"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={toggleOpen}
        >
          {open ? "Hide introduction" : "Show introduction"}
        </button>
      </div>

      <div
        id={panelId}
        role="region"
        aria-labelledby={headingId}
        hidden={!open}
        className="border-t border-white/[0.04] px-4 pb-4 pt-3 md:px-5 md:pb-5"
      >
        <p className="max-w-3xl text-sm leading-relaxed text-zinc-400">
          This panel walks through <strong className="font-medium text-zinc-300">made-up situations</strong>{" "}
          — everyday life, tension, or risk — like flipping{" "}
          <strong className="font-medium text-zinc-300">ethical story cards</strong> in front of a
          research &ldquo;android.&rdquo; Each new scene asks how that prototype would weigh different
          responses. The <strong className="font-medium text-zinc-300">numbers next to each action</strong>{" "}
          are simple hints of <em className="text-zinc-400">better or worse inside this simulator</em>;
          readings for risk, calm, or vulnerability show{" "}
          <strong className="font-medium text-zinc-300">how charged the fictional moment feels</strong>{" "}
          to the model — not a judgment about you.{" "}
          <span className="text-zinc-500">
            None of this is medical or legal advice, or guidance for real decisions; the point is that
            anyone can{" "}
            <strong className="font-medium text-zinc-400">
              peek inside a transparent machine-ethics experiment
            </strong>{" "}
            without formulas or jargon.
          </span>
        </p>

        <p className="mt-4 max-w-3xl border-l-2 border-violet-500/25 pl-4 text-sm leading-relaxed text-zinc-400">
          <strong className="font-medium text-zinc-300">What this adds up to</strong> — In this demo, the{" "}
          <strong className="font-medium text-zinc-300">simulation and the numbers</strong> are what
          <strong className="font-medium text-zinc-300"> determine what happens</strong> for each
          situation: they express{" "}
          <strong className="font-medium text-zinc-300">how the model&apos;s ethical consciousness
          perceives that reality</strong> — how intense the stakes feel, which options look acceptable
          or harmful — and therefore{" "}
          <strong className="font-medium text-zinc-300">how strongly, and in what direction, it would
          tend to react</strong>. That inner logic is not married to a humanoid shell: the same kind
          of agent could be imagined as an <strong className="font-medium text-zinc-300">android</strong>, a{" "}
          <strong className="font-medium text-zinc-300">self-driving car</strong>, or{" "}
          <strong className="font-medium text-zinc-300">another autonomous system</strong>; here you are
          only watching that <strong className="font-medium text-zinc-300">ethical decision layer</strong>{" "}
          stripped down on screen.
        </p>

        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-400">
          <strong className="font-medium text-zinc-300">What you can press</strong> — In the simulator
          below, use the{" "}
          <strong className="font-medium text-zinc-300">clickable controls in the left column</strong>:
          the wide <strong className="font-medium text-zinc-300">Random Situation</strong> bar (dice
          icon), each <strong className="font-medium text-zinc-300">numbered scenario</strong> in the
          list, and — after a random draw — the <strong className="font-medium text-zinc-300">Another</strong>{" "}
          button to draw again. Pipeline tags, charts, and scores are{" "}
          <strong className="font-medium text-zinc-300">read-only</strong> feedback.
        </p>

        <div
          className="mt-3 flex flex-wrap items-center gap-2"
          aria-hidden="true"
        >
          <span className="text-[10px] font-medium uppercase tracking-wider text-zinc-600">
            Pressable style (examples)
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/40 bg-gradient-to-br from-indigo-950/90 to-indigo-900/60 px-2.5 py-1.5 text-[11px] font-bold tracking-wide text-violet-200">
            <span aria-hidden>🎲</span> Random Situation
          </span>
          <span className="inline-flex rounded-md border border-slate-600/60 bg-slate-800/50 px-2.5 py-1.5 text-left text-[11px] font-semibold text-slate-200">
            1. Soda can…
          </span>
          <span className="inline-flex items-center gap-1 rounded-md border border-violet-500/35 bg-indigo-950/70 px-2.5 py-1.5 text-[11px] font-semibold text-violet-200">
            <span aria-hidden>🔄</span> Another
          </span>
        </div>
      </div>
    </section>
  );
}
