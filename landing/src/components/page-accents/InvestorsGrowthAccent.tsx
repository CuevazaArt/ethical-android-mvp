"use client";

import { motion } from "framer-motion";

/**
 * Investors / ecosystem — orbital map: nodes on a path with chords that fade,
 * not a bar chart (avoids collision with “metrics” cliché).
 */
const NODE_ANGLES = [0, 52, 104, 156, 208, 270, 320];

export function InvestorsGrowthAccent() {
  const cx = 100;
  const cy = 36;
  const r = 28;

  return (
    <div
      className="pointer-events-none relative flex h-[5.25rem] w-full items-center justify-center overflow-hidden border-b border-sky-950/25 bg-gradient-to-b from-sky-950/20 via-transparent to-transparent"
      aria-hidden
    >
      <svg
        className="h-full w-full max-w-md"
        viewBox="0 0 200 72"
        fill="none"
        preserveAspectRatio="xMidYMid meet"
      >
        <motion.ellipse
          cx={cx}
          cy={cy}
          rx={r}
          ry={r * 0.42}
          stroke="rgb(56 189 248 / 0.2)"
          strokeWidth="1"
          strokeDasharray="4 6"
          animate={{ strokeDashoffset: [0, -20] }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        />
        {NODE_ANGLES.map((deg, i) => {
          const rad = (deg * Math.PI) / 180;
          const x = cx + r * Math.cos(rad);
          const y = cy + r * 0.42 * Math.sin(rad);
          return (
            <motion.circle
              key={deg}
              cx={x}
              cy={y}
              r="3.5"
              fill="rgb(125 211 252 / 0.5)"
              animate={{ opacity: [0.35, 0.95, 0.35] }}
              transition={{
                duration: 2.8,
                repeat: Infinity,
                delay: i * 0.22,
                ease: "easeInOut",
              }}
            />
          );
        })}
        <motion.line
          x1={cx + r * Math.cos(0)}
          y1={cy}
          x2={cx + r * Math.cos((104 * Math.PI) / 180)}
          y2={cy + r * 0.42 * Math.sin((104 * Math.PI) / 180)}
          stroke="rgb(56 189 248 / 0.25)"
          strokeWidth="1"
          animate={{ opacity: [0.1, 0.55, 0.1] }}
          transition={{ duration: 3.2, repeat: Infinity }}
        />
        <motion.line
          x1={cx + r * Math.cos((156 * Math.PI) / 180)}
          y1={cy + r * 0.42 * Math.sin((156 * Math.PI) / 180)}
          x2={cx + r * Math.cos((270 * Math.PI) / 180)}
          y2={cy + r * 0.42 * Math.sin((270 * Math.PI) / 180)}
          stroke="rgb(167 139 250 / 0.22)"
          strokeWidth="1"
          animate={{ opacity: [0.1, 0.5, 0.1] }}
          transition={{ duration: 3.6, repeat: Infinity, delay: 0.8 }}
        />
      </svg>
    </div>
  );
}
