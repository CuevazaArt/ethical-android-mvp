"use client";

import { motion } from "framer-motion";

/** Soft network — who we are, connection & trust. */
export function AboutPeopleAccent() {
  return (
    <div
      className="pointer-events-none relative h-[5.5rem] w-full overflow-hidden border-b border-white/[0.06] bg-gradient-to-b from-violet-950/25 to-transparent"
      aria-hidden
    >
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 480 72"
        preserveAspectRatio="xMidYMid meet"
        fill="none"
      >
        <motion.line
          x1="72"
          y1="36"
          x2="180"
          y2="36"
          stroke="rgb(167 139 250 / 0.25)"
          strokeWidth="1"
          animate={{ opacity: [0.2, 0.55, 0.2] }}
          transition={{ duration: 4, repeat: Infinity }}
        />
        <motion.line
          x1="180"
          y1="36"
          x2="300"
          y2="28"
          stroke="rgb(167 139 250 / 0.2)"
          strokeWidth="1"
          animate={{ opacity: [0.15, 0.45, 0.15] }}
          transition={{ duration: 3.5, repeat: Infinity, delay: 0.5 }}
        />
        <motion.line
          x1="180"
          y1="36"
          x2="300"
          y2="48"
          stroke="rgb(96 165 250 / 0.2)"
          strokeWidth="1"
          animate={{ opacity: [0.15, 0.4, 0.15] }}
          transition={{ duration: 4.2, repeat: Infinity, delay: 0.2 }}
        />
        {[
          { cx: 72, cy: 36 },
          { cx: 180, cy: 36 },
          { cx: 300, cy: 28 },
          { cx: 300, cy: 48 },
        ].map((p, i) => (
          <motion.circle
            key={`${p.cx}-${p.cy}`}
            cx={p.cx}
            cy={p.cy}
            r="5"
            fill="rgb(167 139 250 / 0.35)"
            animate={{ r: [5, 6.5, 5], opacity: [0.45, 0.9, 0.45] }}
            transition={{ duration: 3 + i * 0.4, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </svg>
    </div>
  );
}
