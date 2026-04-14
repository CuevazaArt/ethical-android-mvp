"use client";

import { motion } from "framer-motion";

const SPARKS = [
  { x: "14%", delay: 0, dur: 4, green: true },
  { x: "32%", delay: 0.6, dur: 3.6, green: false },
  { x: "48%", delay: 1.1, dur: 4.1, green: true },
  { x: "64%", delay: 0.25, dur: 3.7, green: false },
  { x: "78%", delay: 1.4, dur: 4.4, green: true },
  { x: "90%", delay: 0.9, dur: 3.9, green: false },
] as const;

/**
 * Donate — green/orange rising sparks + slow rotating halo + ground glow.
 */
export function DonateRippleAccent() {
  return (
    <div
      className="pointer-events-none relative h-[6.5rem] w-full overflow-hidden border-b border-orange-500/15 bg-gradient-to-t from-emerald-950/25 via-orange-950/10 to-emerald-950/15"
      aria-hidden
    >
      <motion.div
        className="absolute left-1/2 top-1/2 h-32 w-32 -translate-x-1/2 -translate-y-1/2 rounded-full border border-emerald-500/15"
        animate={{ rotate: 360, scale: [1, 1.08, 1] }}
        transition={{ rotate: { duration: 24, repeat: Infinity, ease: "linear" }, scale: { duration: 4, repeat: Infinity } }}
      />
      <motion.div
        className="absolute left-1/2 top-[55%] h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border border-orange-400/20"
        animate={{ rotate: -360 }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
      />

      {SPARKS.map((s, i) => (
        <motion.span
          key={i}
          className={`absolute bottom-0 h-2 w-2 rounded-full blur-[0.5px] ${
            s.green
              ? "bg-gradient-to-t from-emerald-400/60 to-emerald-300/30"
              : "bg-gradient-to-t from-orange-400/65 to-amber-300/35"
          }`}
          style={{ left: s.x, marginLeft: "-4px" }}
          initial={{ y: 0, opacity: 0, scale: 0.6 }}
          animate={{
            y: [-6, -80],
            opacity: [0, 0.9, 0],
            scale: [0.5, 1.05, 0.35],
          }}
          transition={{
            duration: s.dur,
            repeat: Infinity,
            delay: s.delay,
            ease: "easeOut",
            times: [0, 0.12, 1],
          }}
        />
      ))}

      <motion.div
        className="absolute left-1/2 top-3 flex h-5 w-5 -translate-x-1/2 items-center justify-center rounded-md border border-orange-400/35 bg-orange-500/10 text-[10px] font-bold text-orange-300/80"
        animate={{ scale: [1, 1.08, 1], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 2.5, repeat: Infinity }}
      >
        +
      </motion.div>

      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-400/25 via-orange-400/25 to-transparent" />
    </div>
  );
}
