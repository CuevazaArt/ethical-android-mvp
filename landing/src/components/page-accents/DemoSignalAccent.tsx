"use client";

import { motion } from "framer-motion";

/**
 * Demo / control room — radar sweep over a live field (simulation monitor),
 * not a bar chart or document metaphor.
 */
export function DemoSignalAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-[4.5rem] w-full items-center justify-center overflow-hidden border-b border-emerald-950/30 bg-[#040807]"
      aria-hidden
    >
      <div className="relative flex h-14 w-14 items-center justify-center rounded-full border border-emerald-500/25 bg-emerald-950/50 shadow-[inset_0_0_18px_rgba(16,185,129,0.07)]">
        <motion.div
          className="absolute left-1/2 top-1/2 h-7 w-px -translate-x-1/2 -translate-y-full origin-bottom bg-gradient-to-t from-emerald-700/40 via-emerald-400/70 to-emerald-200/90"
          animate={{ rotate: 360 }}
          transition={{ duration: 5.5, repeat: Infinity, ease: "linear" }}
        />
        <div className="h-1.5 w-1.5 rounded-full bg-emerald-400/90 shadow-[0_0_10px_rgba(52,211,153,0.5)]" />
      </div>
      <div className="absolute bottom-2 left-4 flex gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-1 w-3 rounded-sm bg-emerald-600/35"
            animate={{ opacity: [0.2, 0.95, 0.2] }}
            transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.18 }}
          />
        ))}
      </div>
    </div>
  );
}
