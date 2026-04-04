"use client";

import { motion } from "framer-motion";

/** Animated text lines — single document / brief. */
const WIDTHS = [100, 94, 88, 96, 72, 84];

export function OnePagerLinesAccent() {
  return (
    <div
      className="pointer-events-none mt-4 space-y-2 print:hidden"
      aria-hidden
    >
      {WIDTHS.map((w, i) => (
        <motion.div
          key={i}
          className="h-1 rounded-full bg-zinc-600/40"
          style={{ width: `${w}%` }}
          initial={{ opacity: 0.25 }}
          animate={{
            opacity: [0.25, 0.55, 0.3],
            x: [0, 4, 0],
          }}
          transition={{
            duration: 3.5,
            repeat: Infinity,
            delay: i * 0.15,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}
