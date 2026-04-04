"use client";

import { motion } from "framer-motion";

/**
 * About / “Who we are” — three pillars of intent (mission, vision, values):
 * vertical columns with a slow light sheen — institutional, grounded, not a graph.
 */
export function AboutPeopleAccent() {
  return (
    <div
      className="pointer-events-none relative flex h-[4.75rem] w-full items-end justify-center gap-6 overflow-hidden border-b border-amber-950/20 bg-gradient-to-b from-amber-950/15 via-transparent to-transparent px-8 pb-0 pt-3"
      aria-hidden
    >
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="relative h-12 w-2 overflow-hidden rounded-t-md bg-zinc-800/50 ring-1 ring-amber-500/15"
        >
          <motion.div
            className="absolute inset-x-0 bottom-0 top-0 bg-gradient-to-b from-transparent via-amber-400/25 to-transparent"
            initial={{ y: "100%" }}
            animate={{ y: ["100%", "-100%"] }}
            transition={{
              duration: 3.8,
              repeat: Infinity,
              ease: "linear",
              delay: i * 0.9,
            }}
          />
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-1 rounded-t-sm bg-amber-500/35"
            animate={{ opacity: [0.35, 0.85, 0.35] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.25 }}
          />
        </div>
      ))}
    </div>
  );
}
