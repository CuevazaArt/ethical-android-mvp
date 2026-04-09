"""
Short-term conversational memory (STM).

Holds recent turns for coherence; does not replace NarrativeMemory (long-term episodes).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkingMemory:
    """
    Rolling window of user/android exchanges with light state for dialogue.

    - turns: last N items with user text, android reply snippet, and perception signals
    - user_emotional_trend: EMA of hostility-like tension (0–1)
    """

    max_turns: int = 10
    turns: List[Dict[str, Any]] = field(default_factory=list)
    active_topic: Optional[str] = None
    user_emotional_trend: float = 0.5

    def add_turn(
        self,
        user_text: str,
        android_response: str,
        perception_signals: Optional[Dict[str, float]],
        *,
        heavy_kernel: bool = False,
        blocked: bool = False,
    ) -> None:
        sig = perception_signals or {}
        self.turns.append({
            "u": user_text,
            "a": android_response,
            "s": sig,
            "heavy": heavy_kernel,
            "blocked": blocked,
        })
        while len(self.turns) > self.max_turns:
            self.turns.pop(0)

        h = float(sig.get("hostility", 0.0))
        self.user_emotional_trend = max(0.0, min(1.0, 0.7 * self.user_emotional_trend + 0.3 * h))

        if heavy_kernel and user_text:
            self.active_topic = (user_text[:80] + "…") if len(user_text) > 80 else user_text

    def format_context_for_perception(self, max_chars: int = 1200) -> str:
        """Compact transcript for LLM perception (oldest first)."""
        if not self.turns:
            return ""
        lines: List[str] = []
        for t in self.turns:
            u = str(t.get("u", "")).replace("\n", " ").strip()
            a = str(t.get("a", "")).replace("\n", " ").strip()
            if len(a) > 220:
                a = a[:217] + "…"
            lines.append(f"User: {u}\nAndroid: {a}")
        blob = "\n\n".join(lines)
        if len(blob) > max_chars:
            blob = "…" + blob[-(max_chars - 1) :]
        return blob

    def clear(self) -> None:
        self.turns.clear()
        self.active_topic = None
        self.user_emotional_trend = 0.5
