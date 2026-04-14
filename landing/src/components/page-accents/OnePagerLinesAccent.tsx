"use client";

import { motion } from "framer-motion";

const WIDTHS = [88, 92, 78, 94, 66];

/**
 * One-pager — margin (green pulse) + lines with orange segment + caret + corner seal ring.
 */
export function OnePagerLinesAccent() {
  return (
    <div
      className="pointer-events-none relative mt-5 flex gap-3 print:hidden"
      aria-hidden
    >
      <div className="relative shrink-0">
        <motion.div
          className="mt-0.5 w-1 rounded-full bg-gradient-to-b from-emerald-600/60 via-emerald-400/40 to-orange-500/50"
          initial={{ scaleY: 0.35, opacity: 0.5 }}
          animate={{ scaleY: [0.35, 1, 0.92, 1], opacity: [0.45, 0.9, 0.65, 0.85] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
          style={{ height: "5rem", transformOrigin: "top" }}
        />
        <motion.div
          className="absolute -left-1 top-0 h-2 w-2 rounded-full border border-orange-400/50"
          animate={{ rotate: 360, opacity: [0.4, 0.85, 0.4] }}
          transition={{ rotate: { duration: 12, repeat: Infinity, ease: "linear" }, opacity: { duration: 3, repeat: Infinity } }}
        />
      </div>

      <div className="min-w-0 flex-1 space-y-2 pt-0.5">
        {WIDTHS.map((w, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="relative h-1 overflow-hidden rounded-sm bg-zinc-700/30"
              style={{ width: `${w}%` }}
            >
              <motion.div
                className={`absolute inset-y-0 left-0 rounded-sm ${
                  i === 2 ? "bg-orange-400/35" : "bg-emerald-500/25"
                }`}
                initial={{ width: "0%" }}
                animate={{ width: i === 2 ? ["20%", "55%", "30%", "45%"] : ["15%", "70%", "25%", "60%"] }}
                transition={{
                  duration: 5 + i * 0.3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            </div>
            {i === WIDTHS.length - 1 ? (
              <div className="flex items-center gap-1">
                <motion.span
                  className="inline-block h-3 w-0.5 bg-emerald-400/80"
                  animate={{ opacity: [1, 1, 0.15, 0.15, 1] }}
                  transition={{
                    duration: 1.2,
                    repeat: Infinity,
                    times: [0, 0.45, 0.5, 0.9, 1],
                    ease: "linear",
                  }}
                />
                <motion.span
                  className="inline-block h-3 w-0.5 bg-orange-400/70"
                  animate={{ opacity: [0.15, 0.15, 1, 1, 0.15] }}
                  transition={{
                    duration: 1.2,
                    repeat: Infinity,
                    times: [0, 0.45, 0.5, 0.9, 1],
                    ease: "linear",
                  }}
                />
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
