"use client";

import { motion } from "framer-motion";

/**
 * Demo — dual radar (green core + orange ring) + counter sweep + waveform strip.
 */
export function DemoSignalAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-[5.5rem] w-full flex-col items-center justify-center overflow-hidden border-b border-emerald-900/40 bg-[#030806]"
      aria-hidden
    >
      <div className="relative flex items-center justify-center">
        <motion.div
          className="absolute h-[4.25rem] w-[4.25rem] rounded-full border border-orange-500/30"
          animate={{ opacity: [0.35, 0.7, 0.35], scale: [0.96, 1.02, 0.96] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        />
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full border border-emerald-500/35 bg-emerald-950/55 shadow-[inset_0_0_20px_rgba(16,185,129,0.1)]">
          <motion.div
            className="absolute left-1/2 top-1/2 h-7 w-px -translate-x-1/2 -translate-y-full origin-bottom bg-gradient-to-t from-emerald-800/50 via-emerald-400/80 to-emerald-200"
            animate={{ rotate: 360 }}
            transition={{ duration: 5.5, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            className="absolute left-1/2 top-1/2 h-5 w-px -translate-x-1/2 -translate-y-full origin-bottom bg-gradient-to-t from-orange-700/40 to-orange-300/70"
            animate={{ rotate: -360 }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          />
          <div className="h-1.5 w-1.5 rounded-full bg-gradient-to-br from-emerald-300 to-orange-300 shadow-[0_0_12px_rgba(52,211,153,0.45)]" />
        </div>
      </div>

      <div className="absolute bottom-1.5 left-0 right-0 flex h-3 items-end justify-center gap-px px-6">
        {Array.from({ length: 28 }).map((_, i) => (
          <motion.span
            key={i}
            className={`w-0.5 rounded-t-sm ${i % 3 === 0 ? "bg-orange-400/50" : "bg-emerald-500/40"}`}
            initial={{ height: 4 }}
            animate={{
              height: [4, 10 + (i % 5) * 2, 4],
              opacity: [0.35, 0.9, 0.35],
            }}
            transition={{
              duration: 1.4 + (i % 4) * 0.1,
              repeat: Infinity,
              delay: i * 0.05,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <div className="absolute bottom-2 left-4 flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <motion.span
            key={i}
            className={`h-1 w-2.5 rounded-sm ${i % 2 === 0 ? "bg-emerald-500/45" : "bg-orange-400/45"}`}
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </div>
    </div>
  );
}
