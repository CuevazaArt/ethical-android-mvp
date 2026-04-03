"use client";

import { motion } from "framer-motion";

import { MathBlock } from "@/components/MathBlock";

const CORE_MATH = [
  {
    title: "Sigmoid will",
    caption: "Smooth commitment instead of a binary switch; uncertainty I(x) feeds the imagination term.",
    tex: "W(x)=\\dfrac{1}{1+e^{-k(x-x_0)}}+\\lambda\\, I(x)",
  },
  {
    title: "Ethical optimization",
    caption: "Maximize expected ethical impact only over actions that survive the absolute-evil fuse.",
    tex: "x^*=\\arg\\max \\mathbb{E}[\\mathrm{Impact}(x\\mid\\theta)]\\quad\\text{s.t.}\\quad \\mathrm{MalAbs}(x)=\\text{false}",
  },
  {
    title: "Multipolar arbitration",
    caption: "Poles vote with scores V_i; context and sensors rescale weights in real time.",
    tex: "\\mathrm{Score}(a)=\\sum_i w_i(t)\\,V_i(a),\\quad w_i(t)=w_i^{0}\\cdot f(C_t,S_t)",
  },
] as const;

const PREDICATES = [
  {
    title: "MalAbs (hard veto)",
    caption: "If the fuse fires, the action is discarded — no bargaining, no gradient climb past it.",
    tex: "\\forall a:\\ \\mathrm{MalAbs}(a)\\implies \\neg\\,\\mathrm{Permit}(a)",
  },
  {
    title: "Gray zone (deliberation)",
    caption: "High ambiguity or tight margins force deep deliberation, DAO hooks, and audit trails.",
    tex: "\\mathrm{Gray}(s)\\iff \\mathrm{Unc}(s)>\\tau\\ \\lor\\ \\lvert\\Delta\\mathrm{Score}\\rvert<\\varepsilon",
  },
  {
    title: "Epistemic uncertainty",
    caption: "Expected doubt over hypotheses — when it spikes, the kernel slows down instead of faking confidence.",
    tex: "I(x)=\\displaystyle\\int \\bigl(1-P(\\mathrm{ok}\\mid\\theta)\\bigr)\\,P(\\theta\\mid D)\\,d\\theta",
  },
] as const;

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.06 * i, duration: 0.5, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export function TheoryMathShowcase() {
  return (
    <div className="theory-math-showcase mt-14 space-y-14">
      <div>
        <h3 className="text-sm font-semibold tracking-wide text-violet-300/90">
          Signature mathematics
        </h3>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-500">
          The same objects implemented in Python — shown here in standard notation.
        </p>
        <div className="mt-8 grid gap-8 lg:grid-cols-3">
          {CORE_MATH.map((item, i) => (
            <motion.div
              key={item.title}
              custom={i}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-32px" }}
              variants={fadeUp}
              className="rounded-2xl border border-violet-500/20 bg-gradient-to-b from-violet-500/[0.07] to-transparent px-4 py-6 md:px-5"
            >
              <p className="text-xs font-medium uppercase tracking-wider text-violet-400/80">
                {item.title}
              </p>
              <div className="math-display mt-4 min-h-[4.5rem] items-center">
                <MathBlock tex={item.tex} display accessibilityLabel={item.title} />
              </div>
              <p className="mt-4 text-xs leading-relaxed text-zinc-500">{item.caption}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold tracking-wide text-sky-300/90">
          Predicate logic (kernel hooks)
        </h3>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-500">
          Compact logical forms for the non-negotiable gates and ambiguity detectors.
        </p>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {PREDICATES.map((item, i) => (
            <motion.div
              key={item.title}
              custom={i + CORE_MATH.length}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-32px" }}
              variants={fadeUp}
              className="rounded-2xl border border-sky-500/15 bg-white/[0.02] px-4 py-5 md:px-5"
            >
              <p className="text-xs font-medium uppercase tracking-wider text-sky-400/85">
                {item.title}
              </p>
              <div className="math-display-predicate mt-3 min-h-[3.25rem]">
                <MathBlock tex={item.tex} display accessibilityLabel={item.title} />
              </div>
              <p className="mt-3 text-xs leading-relaxed text-zinc-500">{item.caption}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
