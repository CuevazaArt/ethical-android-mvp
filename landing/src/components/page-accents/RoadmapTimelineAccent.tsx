"use client";

import { motion } from "framer-motion";

/**
 * Roadmap — horizontal timeline: past (green) → present → next (orange).
 */
const NODES = [
  { phase: "shipped", green: true },
  { phase: "now", green: true },
  { phase: "next", green: false },
  { phase: "ahead", green: false },
] as const;

export function RoadmapTimelineAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-[5rem] w-full items-center justify-center overflow-hidden border-b border-emerald-900/20 bg-gradient-to-r from-emerald-950/20 via-zinc-950/40 to-orange-950/25"
      aria-hidden
    >
      <div className="relative flex w-full max-w-xl items-center px-10">
        <motion.div
          className="absolute left-10 right-10 top-1/2 h-px -translate-y-1/2 bg-gradient-to-r from-emerald-500/40 via-zinc-500/30 to-orange-400/45"
          initial={{ scaleX: 0.85, opacity: 0.5 }}
          animate={{ scaleX: [0.88, 1, 0.88], opacity: [0.45, 0.9, 0.45] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformOrigin: "center" }}
        />
        <div className="relative z-[1] flex w-full justify-between">
          {NODES.map((n, i) => (
            <motion.div
              key={n.phase}
              className={`flex h-3 w-3 rounded-full border-2 ${
                n.green
                  ? "border-emerald-400/60 bg-emerald-500/30 shadow-[0_0_10px_rgba(52,211,153,0.35)]"
                  : "border-orange-400/60 bg-orange-500/25 shadow-[0_0_10px_rgba(251,146,60,0.3)]"
              }`}
              animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
              transition={{
                duration: 2.2,
                repeat: Infinity,
                delay: i * 0.35,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
