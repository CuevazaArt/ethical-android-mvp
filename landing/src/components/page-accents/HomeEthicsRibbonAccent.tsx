"use client";

import { motion } from "framer-motion";

/** Subtle flowing ribbon under the main nav — ethics as continuous deliberation. */
export function HomeEthicsRibbonAccent() {
  return (
    <div
      className="pointer-events-none relative z-[2] h-0 w-full overflow-visible"
      aria-hidden
    >
      <motion.div
        className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-violet-500/45 to-transparent"
        initial={{ scaleX: 0.3, opacity: 0.4 }}
        animate={{
          scaleX: [0.35, 1, 0.35],
          opacity: [0.35, 0.85, 0.35],
        }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        style={{ transformOrigin: "center" }}
      />
    </div>
  );
}
