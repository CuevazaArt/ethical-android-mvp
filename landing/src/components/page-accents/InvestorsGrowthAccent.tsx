"use client";

import { motion } from "framer-motion";

/** Rising bars — scope, traction, ecosystem upside. */
const BAR_HEIGHTS = [32, 52, 38, 68, 48, 58];

export function InvestorsGrowthAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-20 w-full items-end justify-center gap-1.5 overflow-hidden border-b border-white/[0.06] bg-gradient-to-b from-emerald-950/15 to-transparent px-8 pb-2 pt-4 sm:gap-2"
      aria-hidden
    >
      {BAR_HEIGHTS.map((h, i) => (
        <motion.div
          key={i}
          className="w-2 rounded-t-sm bg-gradient-to-t from-violet-600/50 to-emerald-400/45 sm:w-2.5"
          initial={{ height: 10 }}
          animate={{ height: [12, h, 14, h * 0.85, h] }}
          transition={{
            duration: 5,
            repeat: Infinity,
            delay: i * 0.12,
            ease: "easeInOut",
            times: [0, 0.25, 0.5, 0.75, 1],
          }}
        />
      ))}
    </div>
  );
}
