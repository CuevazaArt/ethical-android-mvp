"use client";

import { motion } from "framer-motion";

/**
 * One-pager / print brief — editorial page: margin rule + body lines + blinking
 * caret (press & due diligence), not generic shimmer blocks.
 */
const WIDTHS = [88, 92, 78, 94, 66];

export function OnePagerLinesAccent() {
  return (
    <div
      className="pointer-events-none relative mt-5 flex gap-3 print:hidden"
      aria-hidden
    >
      <motion.div
        className="mt-0.5 w-px shrink-0 bg-zinc-600/50"
        initial={{ scaleY: 0.3, opacity: 0.4 }}
        animate={{ scaleY: [0.3, 1, 0.95, 1], opacity: [0.4, 0.75, 0.65, 0.75] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{ height: "4.5rem", transformOrigin: "top" }}
      />
      <div className="min-w-0 flex-1 space-y-2 pt-0.5">
        {WIDTHS.map((w, i) => (
          <div key={i} className="flex items-center gap-2">
            <motion.div
              className="h-1 rounded-sm bg-zinc-600/35"
              style={{ width: `${w}%` }}
              initial={{ opacity: 0.2 }}
              animate={{ opacity: [0.2, 0.45, 0.25] }}
              transition={{
                duration: 4,
                repeat: Infinity,
                delay: i * 0.12,
                ease: "easeInOut",
              }}
            />
            {i === WIDTHS.length - 1 ? (
              <motion.span
                className="inline-block h-3 w-0.5 bg-violet-400/70"
                animate={{ opacity: [1, 1, 0.2, 0.2, 1] }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  times: [0, 0.45, 0.5, 0.9, 1],
                  ease: "linear",
                }}
              />
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
