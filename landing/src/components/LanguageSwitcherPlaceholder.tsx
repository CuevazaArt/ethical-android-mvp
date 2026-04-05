"use client";

/**
 * Placeholder until i18n / locale routing is implemented.
 */
export function LanguageSwitcherPlaceholder() {
  return (
    <button
      type="button"
      disabled
      aria-label="Language: English only for now. Spanish and other locales planned."
      title="Language selection (e.g. Spanish) — coming in a future release"
      className="inline-flex shrink-0 cursor-not-allowed items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.04] px-2.5 py-1.5 text-xs font-medium text-zinc-500 opacity-90"
    >
      <span aria-hidden className="text-[13px]">
        🌐
      </span>
      <span>EN</span>
      <span className="hidden text-[10px] font-normal text-zinc-600 sm:inline">
        · ES soon
      </span>
    </button>
  );
}
