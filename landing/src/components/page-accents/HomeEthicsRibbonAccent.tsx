"use client";

import { motion } from "framer-motion";

/**
 * Home / landing — “portal of consciousness”: twin arcs orbit in opposite
 * directions (mind ↔ embodiment). Not a bar chart, not a network — a threshold.
 */
export function HomeEthicsRibbonAccent() {
  return (
    <div
      className="pointer-events-none relative z-[2] flex h-14 w-full items-center justify-center overflow-hidden"
      aria-hidden
    >
      <div className="relative h-12 w-48 md:w-56">
        <motion.svg
          className="absolute inset-0 h-full w-full text-violet-400/50"
          viewBox="0 0 200 48"
          fill="none"
          aria-hidden
        >
          <motion.path
            d="M 20 38 A 80 28 0 0 1 180 38"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinecap="round"
            animate={{ rotate: [0, 3, 0, -3, 0] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            style={{ transformOrigin: "100px 38px" }}
          />
          <motion.path
            d="M 30 12 A 70 22 0 0 0 170 12"
            stroke="url(#homeArcGrad)"
            strokeWidth="1"
            strokeLinecap="round"
            opacity={0.65}
            animate={{ rotate: [0, -4, 0, 4, 0] }}
            transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
            style={{ transformOrigin: "100px 12px" }}
          />
          <defs>
            <linearGradient id="homeArcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(167 139 250)" stopOpacity="0.2" />
              <stop offset="50%" stopColor="rgb(244 114 182)" stopOpacity="0.55" />
              <stop offset="100%" stopColor="rgb(167 139 250)" stopOpacity="0.2" />
            </linearGradient>
          </defs>
        </motion.svg>
        <motion.div
          className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-200/80 shadow-[0_0_14px_rgba(221,214,254,0.6)]"
          animate={{ scale: [1, 1.4, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}
