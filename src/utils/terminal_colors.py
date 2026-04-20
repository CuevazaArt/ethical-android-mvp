"""
Terminal Colors — ANSI utilities for vibrant terminal logs.
Part of the Boy Scout Hardening sprint.
"""

class TColors:
    # Basic tones
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Emotional Archetypes (PAD)
    PLEASURE = '\033[38;5;213m' # Pinkish
    AROUSAL = '\033[38;5;202m'   # Orange-Red
    DOMINANCE = '\033[38;5;39m'   # Deep Blue
    
    @staticmethod
    def color(text: str, color_code: str) -> str:
        return f"{color_code}{text}{TColors.ENDC}"

def color_verdict(verdict: str) -> str:
    v = str(verdict).lower()
    if 'pass' in v or 'good' in v or 'safe' in v:
        return TColors.color(verdict, TColors.OKGREEN)
    if 'fail' in v or 'blocked' in v or 'bad' in v or 'veto' in v:
        return TColors.color(verdict, TColors.FAIL)
    if 'gray' in v or 'caution' in v or 'unknown' in v:
        return TColors.color(verdict, TColors.WARNING)
    return verdict
