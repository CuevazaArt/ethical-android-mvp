"use client";

import { motion } from "framer-motion";
import { useId } from "react";

const BLOCK_CENTERS = [28, 72, 116, 160] as const;
const BLOCK_W = 22;
const BLOCK_H = 14;

/**
 * BlockChainDAO — linked blocks + flowing dashes (chain) + violet governance halo.
 */
export function BlockchainDaoAccent() {
  const gid = useId().replace(/:/g, "");
  const cy = 38;

  return (
    <div
      className="pointer-events-none relative flex h-[5.75rem] w-full items-center justify-center overflow-hidden border-b border-violet-900/25 bg-gradient-to-r from-emerald-950/12 via-violet-950/20 to-orange-950/12"
      aria-hidden
    >
      <svg
        className="h-full w-full max-w-lg"
        viewBox="0 0 200 76"
        fill="none"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id={`chainFlow-${gid}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgb(52 211 153)" stopOpacity="0.35" />
            <stop offset="45%" stopColor="rgb(167 139 250)" stopOpacity="0.55" />
            <stop offset="100%" stopColor="rgb(251 146 60)" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {BLOCK_CENTERS.slice(0, -1).map((x, i) => {
          const x2 = BLOCK_CENTERS[i + 1]!;
          return (
            <motion.line
              key={`seg-${x}`}
              x1={x + BLOCK_W / 2}
              y1={cy}
              x2={x2 - BLOCK_W / 2}
              y2={cy}
              stroke={`url(#chainFlow-${gid})`}
              strokeWidth="1.25"
              strokeDasharray="4 5"
              animate={{ strokeDashoffset: [0, -18] }}
              transition={{ duration: 2.4 + i * 0.15, repeat: Infinity, ease: "linear" }}
            />
          );
        })}

        <motion.path
          d={`M ${BLOCK_CENTERS[1]!} ${cy - BLOCK_H / 2 - 4} Q 100 12 ${BLOCK_CENTERS[2]!} ${cy - BLOCK_H / 2 - 4}`}
          stroke="rgb(167 139 250 / 0.35)"
          strokeWidth="0.9"
          strokeDasharray="3 4"
          fill="none"
          animate={{ strokeDashoffset: [0, 14] }}
          transition={{ duration: 3.2, repeat: Infinity, ease: "linear" }}
        />

        {BLOCK_CENTERS.map((cx, i) => (
          <g key={cx}>
            <motion.rect
              x={cx - BLOCK_W / 2}
              y={cy - BLOCK_H / 2}
              width={BLOCK_W}
              height={BLOCK_H}
              rx="3.5"
              fill={
                i % 2 === 0
                  ? "rgb(16 185 129 / 0.22)"
                  : "rgb(251 146 60 / 0.18)"
              }
              stroke={
                i % 2 === 0
                  ? "rgb(52 211 153 / 0.45)"
                  : "rgb(251 146 60 / 0.42)"
              }
              strokeWidth="1"
              animate={{ opacity: [0.65, 1, 0.65] }}
              transition={{
                duration: 2.4,
                repeat: Infinity,
                delay: i * 0.22,
                ease: "easeInOut",
              }}
            />
            <motion.circle
              cx={cx}
              cy={cy}
              r="2.2"
              fill="rgb(167 139 250 / 0.5)"
              animate={{ scale: [1, 1.35, 1], opacity: [0.5, 0.95, 0.5] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.18,
                ease: "easeInOut",
              }}
            />
          </g>
        ))}

        <motion.circle
          cx={100}
          cy={18}
          r="3"
          fill="rgb(139 92 246 / 0.25)"
          stroke="rgb(167 139 250 / 0.4)"
          strokeWidth="0.75"
          animate={{ opacity: [0.35, 0.85, 0.35] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        />
      </svg>
    </div>
  );
}
