"use client";

import { motion } from "framer-motion";

/** Scan line + telemetry dots — interactive dashboard metaphor. */
export function DemoSignalAccent() {
  return (
    <div
      className="pointer-events-none relative h-10 w-full overflow-hidden border-b border-white/[0.06] bg-[#07070c]"
      aria-hidden
    >
      <div className="absolute inset-0 flex items-center justify-center gap-3 opacity-60">
        {[0, 1, 2, 3, 4].map((i) => (
          <motion.span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-emerald-400/80"
            animate={{ opacity: [0.2, 1, 0.2], scale: [0.85, 1.15, 0.85] }}
            transition={{
              duration: 1.4,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
      <motion.div
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent shadow-[0_0_12px_rgba(34,211,238,0.35)]"
        initial={{ top: "10%" }}
        animate={{ top: ["8%", "92%", "8%"] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}
