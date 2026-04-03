"use client";

import katex from "katex";
import "katex/dist/katex.min.css";
import { useEffect, useRef } from "react";

type MathBlockProps = {
  tex: string;
  display?: boolean;
  className?: string;
  /** Short description for assistive tech (the visual is duplicated by nearby captions). */
  accessibilityLabel?: string;
};

/**
 * Renders a LaTeX string with KaTeX (client-only).
 */
export function MathBlock({
  tex,
  display = true,
  className = "",
  accessibilityLabel = "Mathematical expression",
}: MathBlockProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    try {
      katex.render(tex, el, {
        displayMode: display,
        throwOnError: false,
        strict: "ignore",
      });
    } catch {
      el.textContent = tex;
    }
  }, [tex, display]);

  return (
    <div
      ref={ref}
      className={`min-w-0 overflow-x-auto py-1 ${display ? "flex justify-center" : "inline-flex"} ${className}`}
      role="img"
      aria-label={accessibilityLabel}
    />
  );
}
