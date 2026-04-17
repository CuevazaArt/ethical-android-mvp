"""
Utility for ANSI terminal colors and formatting.
"""

from __future__ import annotations

import os
import sys

# Windows terminal support for ANSI escape codes
def _enable_windows_ansi():
    if sys.platform != "win32":
        return
    import ctypes
    kernel32 = ctypes.windll.kernel32
    # 7 = STD_OUTPUT_HANDLE
    # 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

if os.environ.get("KERNEL_TERM_COLOR", "1") == "1":
    try:
        _enable_windows_ansi()
    except Exception:
        pass

class Term:
    """ANSI color codes for the Ethos Kernel."""
    
    # Text colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    B_RED = "\033[91m"
    B_GREEN = "\033[92m"
    B_YELLOW = "\033[93m"
    B_BLUE = "\033[94m"
    B_MAGENTA = "\033[95m"
    B_CYAN = "\033[96m"
    B_WHITE = "\033[97m"
    
    # Backgrounds
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    
    @classmethod
    def color(cls, text: str, color_code: str) -> str:
        if os.environ.get("KERNEL_TERM_COLOR", "1") == "0":
            return text
        return f"{color_code}{text}{cls.RESET}"

    @classmethod
    def highlight_decision(cls, mode: str) -> str:
        if mode == "D_fast":
            return cls.color(mode, cls.B_GREEN + cls.BOLD)
        if mode == "D_delib":
            return cls.color(mode, cls.B_CYAN + cls.BOLD)
        if mode == "gray_zone":
            return cls.color(mode, cls.B_YELLOW + cls.BOLD)
        return cls.color(mode, cls.BOLD)

    @classmethod
    def highlight_impact(cls, val: float) -> str:
        color = cls.RESET
        if val > 0.5:
            color = cls.B_GREEN
        elif val > 0.1:
            color = cls.GREEN
        elif val < -0.5:
            color = cls.B_RED
        elif val < -0.1:
            color = cls.RED
        return cls.color(f"{val:+.3f}", color)
