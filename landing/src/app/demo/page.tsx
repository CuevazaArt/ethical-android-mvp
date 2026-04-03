import Link from "next/link";

export default function DemoPage() {
  return (
    <div className="flex h-dvh flex-col bg-[#050508]">
      <header className="flex shrink-0 items-center justify-between border-b border-white/[0.08] px-4 py-3 md:px-5">
        <Link
          href="/"
          className="text-sm font-medium text-violet-300 transition hover:text-white"
        >
          ← Back
        </Link>
        <span className="text-xs text-zinc-500">Ethical Android — dashboard</span>
      </header>

      <section
        aria-labelledby="demo-intro-heading"
        lang="en"
        className="shrink-0 border-b border-white/[0.06] bg-[#07070c] px-4 py-4 md:px-5 md:py-5"
      >
        <h1
          id="demo-intro-heading"
          className="text-base font-semibold tracking-tight text-zinc-100 md:text-lg"
        >
          What you&apos;re seeing
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-400">
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
            anyone can <strong className="font-medium text-zinc-400">peek inside a transparent machine-ethics experiment</strong>{" "}
            without formulas or jargon.
          </span>
        </p>
      </section>

      <iframe
        src="/dashboard.html"
        title="Ethical Android interactive dashboard"
        className="min-h-0 w-full flex-1 border-0 bg-black"
      />
    </div>
  );
}
