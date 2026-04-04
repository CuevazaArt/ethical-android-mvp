"use client";

import { motion } from "framer-motion";

/** Gentle outward ripples — support & community reach. */
export function DonateRippleAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-24 w-full items-center justify-center overflow-hidden border-b border-white/[0.06] bg-gradient-to-b from-violet-950/20 to-transparent"
      aria-hidden
    >
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="absolute rounded-full border border-violet-400/25"
          initial={{ width: 32, height: 32, opacity: 0.5 }}
          animate={{
            width: 220,
            height: 220,
            opacity: 0,
          }}
          transition={{
            duration: 3.2,
            repeat: Infinity,
            delay: i * 1.05,
            ease: "easeOut",
          }}
        />
      ))}
      <motion.div
        className="relative z-[1] h-2 w-2 rounded-full bg-violet-400/70 shadow-[0_0_20px_rgba(167,139,250,0.5)]"
        animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </div>
  );
}
