"use client";

import { motion } from "framer-motion";

/**
 * Donate / nurture — small “sparks” rise and fade (seeds, support lifting work),
 * not concentric rings like a sonar ping.
 */
const SPARKS = [
  { x: "18%", delay: 0, dur: 4 },
  { x: "38%", delay: 0.7, dur: 3.4 },
  { x: "52%", delay: 1.2, dur: 4.2 },
  { x: "68%", delay: 0.3, dur: 3.8 },
  { x: "82%", delay: 1.6, dur: 4.5 },
] as const;

export function DonateRippleAccent() {
  return (
    <div
      className="pointer-events-none relative h-24 w-full overflow-hidden border-b border-rose-950/20 bg-gradient-to-t from-rose-950/10 via-transparent to-violet-950/10"
      aria-hidden
    >
      {SPARKS.map((s, i) => (
        <motion.span
          key={i}
          className="absolute bottom-0 h-2 w-2 rounded-full bg-gradient-to-t from-rose-400/50 to-violet-300/40 blur-[0.5px]"
          style={{ left: s.x, marginLeft: "-4px" }}
          initial={{ y: 0, opacity: 0, scale: 0.6 }}
          animate={{
            y: [-8, -72],
            opacity: [0, 0.85, 0],
            scale: [0.5, 1, 0.4],
          }}
          transition={{
            duration: s.dur,
            repeat: Infinity,
            delay: s.delay,
            ease: "easeOut",
            times: [0, 0.15, 1],
          }}
        />
      ))}
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-rose-500/20 to-transparent" />
    </div>
  );
}
