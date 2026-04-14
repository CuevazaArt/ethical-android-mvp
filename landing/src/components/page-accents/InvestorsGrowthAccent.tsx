"use client";

import { motion } from "framer-motion";
import { useId } from "react";

const NODE_ANGLES = [0, 52, 104, 156, 208, 270, 320];

/**
 * Investors — dual orbit (sky + orange), alternating node colors, extra cross-chords, center pulse.
 */
export function InvestorsGrowthAccent() {
  const gradId = useId().replace(/:/g, "");
  const cx = 100;
  const cy = 38;
  const r = 30;
  const r2 = 18;

  return (
    <div
      className="pointer-events-none relative flex h-[6rem] w-full items-center justify-center overflow-hidden border-b border-emerald-900/25 bg-gradient-to-b from-emerald-950/15 via-orange-950/10 to-transparent"
      aria-hidden
    >
      <svg
        className="h-full w-full max-w-lg"
        viewBox="0 0 200 76"
        fill="none"
        preserveAspectRatio="xMidYMid meet"
      >
        <motion.ellipse
          cx={cx}
          cy={cy}
          rx={r}
          ry={r * 0.4}
          stroke="rgb(52 211 153 / 0.28)"
          strokeWidth="1"
          strokeDasharray="5 7"
          animate={{ strokeDashoffset: [0, -24] }}
          transition={{ duration: 7, repeat: Infinity, ease: "linear" }}
        />
        <motion.ellipse
          cx={cx}
          cy={cy}
          rx={r2}
          ry={r2 * 0.38}
          stroke="rgb(251 146 60 / 0.35)"
          strokeWidth="1"
          strokeDasharray="3 5"
          animate={{ strokeDashoffset: [0, 18] }}
          transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
        />

        <motion.circle
          cx={cx}
          cy={cy}
          r="4"
          fill="rgb(16 185 129 / 0.45)"
          stroke="rgb(251 146 60 / 0.5)"
          strokeWidth="0.75"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2.4, repeat: Infinity }}
        />

        {NODE_ANGLES.map((deg, i) => {
          const rad = (deg * Math.PI) / 180;
          const x = cx + r * Math.cos(rad);
          const y = cy + r * 0.4 * Math.sin(rad);
          const green = i % 2 === 0;
          return (
            <motion.circle
              key={deg}
              cx={x}
              cy={y}
              r="3.5"
              fill={green ? "rgb(52 211 153 / 0.55)" : "rgb(251 146 60 / 0.55)"}
              animate={{ opacity: [0.4, 0.95, 0.4] }}
              transition={{
                duration: 2.6,
                repeat: Infinity,
                delay: i * 0.18,
                ease: "easeInOut",
              }}
            />
          );
        })}

        <motion.line
          x1={cx + r * Math.cos(0)}
          y1={cy}
          x2={cx + r * Math.cos((120 * Math.PI) / 180)}
          y2={cy + r * 0.4 * Math.sin((120 * Math.PI) / 180)}
          stroke="rgb(52 211 153 / 0.3)"
          strokeWidth="1"
          animate={{ opacity: [0.15, 0.6, 0.15] }}
          transition={{ duration: 3, repeat: Infinity }}
        />
        <motion.line
          x1={cx + r * Math.cos((200 * Math.PI) / 180)}
          y1={cy + r * 0.4 * Math.sin((200 * Math.PI) / 180)}
          x2={cx + r * Math.cos((300 * Math.PI) / 180)}
          y2={cy + r * 0.4 * Math.sin((300 * Math.PI) / 180)}
          stroke="rgb(251 146 60 / 0.32)"
          strokeWidth="1"
          animate={{ opacity: [0.12, 0.55, 0.12] }}
          transition={{ duration: 3.4, repeat: Infinity, delay: 0.5 }}
        />
        <motion.line
          x1={cx}
          y1={cy}
          x2={cx + r * Math.cos((52 * Math.PI) / 180)}
          y2={cy + r * 0.4 * Math.sin((52 * Math.PI) / 180)}
          stroke={`url(#invGrad-${gradId})`}
          strokeWidth="0.75"
          animate={{ opacity: [0.2, 0.65, 0.2] }}
          transition={{ duration: 2.8, repeat: Infinity, delay: 0.2 }}
        />
        <defs>
          <linearGradient id={`invGrad-${gradId}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgb(52 211 153)" stopOpacity="0.4" />
            <stop offset="100%" stopColor="rgb(251 146 60)" stopOpacity="0.45" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
