"""
Structured one-line monologue for logs / debug — not a duplicate of KernelDecision JSON.

Compresses salience focus, reflection tension, PAD archetype, and mode into a
single grep-friendly line.

See docs/discusion/PROPUESTA_INTEGRACION_APORTES_V6.md (Fase 5).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.kernel import KernelDecision


def compose_monologue_line(d: Any, episode_id: Optional[str] = None) -> str:
    """
    Single-line summary for streaming logs. Does not replace format_decision.
    """
    if d.blocked:
        return "[MONO] blocked=1"

    parts = ["[MONO]", f"action={d.final_action}", f"mode={d.decision_mode}"]

    if episode_id:
        parts.append(f"ep={episode_id}")

    if d.salience is not None:
        parts.append(f"focus={d.salience.dominant_focus}")

    if d.reflection is not None:
        parts.append(f"tension={d.reflection.conflict_level}")

    if d.affect is not None:
        parts.append(f"pad_archet={d.affect.dominant_archetype_id}")

    return " ".join(parts)
