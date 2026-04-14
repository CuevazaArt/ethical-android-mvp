"use client";

import { motion } from "framer-motion";

/**
 * About — three pillars + bridging arc (orange) + flanking green pulses + orbit dots.
 */
export function AboutPeopleAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-[5.75rem] w-full items-end justify-center gap-6 overflow-hidden border-b border-orange-500/15 bg-gradient-to-b from-emerald-950/20 via-amber-950/10 to-transparent px-8 pb-1 pt-3"
      aria-hidden
    >
      <motion.div
        className="absolute left-[8%] top-1/2 h-16 w-1 -translate-y-1/2 rounded-full bg-gradient-to-b from-emerald-400/0 via-emerald-400/35 to-emerald-500/0"
        animate={{ opacity: [0.25, 0.85, 0.25], scaleY: [0.7, 1.05, 0.7] }}
        transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute right-[8%] top-1/2 h-16 w-1 -translate-y-1/2 rounded-full bg-gradient-to-b from-orange-400/0 via-orange-400/40 to-orange-500/0"
        animate={{ opacity: [0.3, 0.9, 0.3], scaleY: [0.85, 1.1, 0.85] }}
        transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}
      />

      <svg
        className="pointer-events-none absolute bottom-7 left-1/2 h-8 w-48 -translate-x-1/2 md:w-56"
        viewBox="0 0 240 32"
        fill="none"
        aria-hidden
      >
        <motion.path
          d="M 24 28 Q 120 4 216 28"
          stroke="rgb(251 146 60 / 0.45)"
          strokeWidth="1.25"
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0.3, opacity: 0.4 }}
          animate={{ pathLength: [0.35, 1, 0.35], opacity: [0.35, 0.75, 0.35] }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        />
      </svg>

      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="relative z-[1] h-14 w-2.5 overflow-hidden rounded-t-md bg-zinc-800/55 ring-1 ring-emerald-500/20"
        >
          <motion.div
            className="absolute inset-x-0 bottom-0 top-0 bg-gradient-to-b from-transparent via-orange-400/30 to-transparent"
            initial={{ y: "100%" }}
            animate={{ y: ["100%", "-100%"] }}
            transition={{
              duration: 3.6,
              repeat: Infinity,
              ease: "linear",
              delay: i * 0.85,
            }}
          />
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-1 rounded-t-sm bg-gradient-to-r from-emerald-400/50 to-orange-400/50"
            animate={{ opacity: [0.4, 0.95, 0.4] }}
            transition={{ duration: 2.2, repeat: Infinity, delay: i * 0.2 }}
          />
        </div>
      ))}

      {[0, 1, 2, 3].map((i) => (
        <motion.span
          key={`dot-${i}`}
          className="absolute bottom-2 h-1 w-1 rounded-full bg-emerald-400/70"
          style={{ left: `${22 + i * 18}%` }}
          animate={{ y: [0, -6, 0], opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.35 }}
        />
      ))}
    </div>
  );
}
