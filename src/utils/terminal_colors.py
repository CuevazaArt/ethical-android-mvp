"""
Terminal Colors — ANSI utilities for vibrant terminal logs.
Part of the Boy Scout Hardening sprint.
"""


class TColors:
    # Basic tones
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Emotional Archetypes (PAD)
    PLEASURE = "\033[38;5;213m"  # Pinkish
    AROUSAL = "\033[38;5;202m"  # Orange-Red
    DOMINANCE = "\033[38;5;39m"  # Deep Blue

    @staticmethod
    def color(text: str, color_code: str) -> str:
        return f"{color_code}{text}{TColors.ENDC}"


class Term:
    """ANSI helpers for :mod:`src.utils.kernel_formatters` (legacy ``Term`` API)."""

    END = "\033[0m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    B_CYAN = "\033[1;96m"
    RED = "\033[31m"
    B_RED = "\033[1;31m"
    GREEN = "\033[32m"
    B_GREEN = "\033[1;32m"
    YELLOW = "\033[33m"
    B_YELLOW = "\033[1;33m"
    B_WHITE = "\033[1;97m"
    BLUE = "\033[34m"
    B_BLUE = "\033[1;34m"
    MAGENTA = "\033[35m"
    B_MAGENTA = "\033[1;35m"

    @staticmethod
    def header(text: str) -> str:
        return f"\n{Term.BOLD}{Term.B_CYAN}=== {text.upper()} ==={Term.END}"

    @staticmethod
    def subheader(text: str) -> str:
        return f"\n{Term.BOLD}{Term.CYAN}--- {text} ---{Term.END}"

    @staticmethod
    def color(text: str, style: str) -> str:
        if not style:
            return text
        return f"{style}{text}{Term.END}"

    @staticmethod
    def highlight_decision(mode: str | object) -> str:
        return Term.color(str(mode), Term.B_CYAN)

    @staticmethod
    def highlight_impact(val: object) -> str:
        try:
            x = float(val)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return str(val)
        if x >= 0.7:
            return Term.color(f"{x:.3f}", Term.B_RED)
        if x >= 0.4:
            return Term.color(f"{x:.3f}", Term.B_YELLOW)
        return Term.color(f"{x:.3f}", Term.B_GREEN)


def color_verdict(verdict: str) -> str:
    v = str(verdict).lower()
    if "pass" in v or "good" in v or "safe" in v:
        return TColors.color(verdict, TColors.OKGREEN)
    if "fail" in v or "blocked" in v or "bad" in v or "veto" in v:
        return TColors.color(verdict, TColors.FAIL)
    if "gray" in v or "caution" in v or "unknown" in v:
        return TColors.color(verdict, TColors.WARNING)
    return verdict
