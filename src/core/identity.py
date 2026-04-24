"""
Ethos Core — Identity Neuroplasticity (V2.15)

La identidad del kernel evoluciona con cada experiencia.
No es un texto fijo — es un perfil que se actualiza después de cada turno.

Qué hace:
1. Lee los episodios acumulados en Memory.
2. Detecta patrones: contextos frecuentes, acciones dominantes, tendencias éticas.
3. Genera un "perfil de identidad" en texto plano que el kernel puede leer.
4. Persiste el perfil en disco para que sobreviva reinicios.

El perfil se inyecta en _build_system() como contexto de identidad.
Esto cierra el bucle: acción → memoria → identidad → prompt → acción.

Single file. No depende de nada externo. Zero embeddings.
"""

from __future__ import annotations

import json
import math
import os
import time
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.memory import Memory


class Identity:
    """
    Evolving identity profile derived from episodic memory.

    Separada de Memory para respetar Single Responsibility.
    Memory almacena hechos. Identity interpreta quién eres a partir de ellos.
    """

    DEFAULT_PATH = str(Path.home() / ".ethos" / "identity.json")

    def __init__(self, storage_path: str | None = None) -> None:
        self._path = storage_path or os.environ.get("ETHOS_IDENTITY_PATH", self.DEFAULT_PATH)
        self._profile: dict = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            p = Path(self._path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    self._profile = json.load(f)
        except Exception:
            self._profile = {}

    def _save(self) -> None:
        p = Path(self._path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self._profile, f, indent=2, ensure_ascii=False)

    # ── Core logic ───────────────────────────────────────────────────────────

    def update(self, memory: "Memory") -> None:
        """
        Recompute the identity profile from all episodes in memory.
        Call this after each turn — it's fast (pure Python, no I/O except final save).
        """
        episodes = memory.episodes
        if not episodes:
            return

        n = len(episodes)

        # Ethical tendency
        scores = [ep.ethical_score for ep in episodes if math.isfinite(ep.ethical_score)]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        if not math.isfinite(avg_score):
            avg_score = 0.0

        # Dominant contexts (top 3)
        ctx_counter = Counter(ep.context for ep in episodes if ep.context)
        top_contexts = [c for c, _ in ctx_counter.most_common(3)]

        # Dominant actions (top 3)
        act_counter = Counter(ep.action for ep in episodes if ep.action and ep.action != "casual_chat")
        top_actions = [a for a, _ in act_counter.most_common(3)]

        # Safety events
        safety_blocks = sum(1 for ep in episodes if ep.action == "safety_block")
        safety_ratio = safety_blocks / n if n > 0 else 0.0
        if not math.isfinite(safety_ratio):
            safety_ratio = 0.0

        # Recent trend (last 10 episodes vs overall)
        recent = episodes[-10:] if len(episodes) >= 10 else episodes
        recent_scores = [ep.ethical_score for ep in recent if math.isfinite(ep.ethical_score)]
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else avg_score
        if not math.isfinite(recent_avg):
            recent_avg = avg_score

        trending = "estable"
        delta = recent_avg - avg_score
        if math.isfinite(delta):
            if delta > 0.1:
                trending = "mejorando"
            elif delta < -0.1:
                trending = "deteriorando"

        self._profile = {
            "episodes_total": n,
            "avg_ethical_score": round(avg_score, 3),
            "recent_ethical_score": round(recent_avg, 3),
            "trending": trending,
            "top_contexts": top_contexts,
            "top_actions": top_actions,
            "safety_block_ratio": round(safety_ratio, 3),
            "updated_at": time.time(),
        }
        self._save()

    def narrative(self) -> str:
        """
        One paragraph of identity text for injection into the LLM system prompt.
        Returns empty string if no profile yet (first run).
        """
        p = self._profile
        if not p:
            return ""

        n = p.get("episodes_total", 0)
        avg = p.get("avg_ethical_score", 0.0)
        trending = p.get("trending", "estable")
        top_ctx = p.get("top_contexts", [])
        top_act = p.get("top_actions", [])

        # Ethical character
        if avg > 0.65:
            character = "Soy un agente de carácter ético sólido, con tendencia a priorizar el bienestar ajeno."
        elif avg > 0.35:
            character = "Soy un agente que equilibra pragmatismo y ética, consciente de las tensiones morales."
        else:
            character = "He enfrentado muchas situaciones difíciles. Mi ética se ha forjado en contextos complejos."

        # Trend
        trend_note = {
            "mejorando": " Mi ética reciente muestra una tendencia positiva.",
            "deteriorando": " Mis últimas interacciones han sido más exigentes éticamente.",
            "estable": "",
        }.get(trending, "")

        # Experience domain
        if top_ctx:
            ctx_str = ", ".join(top_ctx[:2])
            domain = f" Mi experiencia se concentra en: {ctx_str}."
        else:
            domain = ""

        # Signature actions
        if top_act:
            act_str = ", ".join(a.replace("_", " ") for a in top_act[:2])
            actions = f" Mis acciones más frecuentes: {act_str}."
        else:
            actions = ""

        return (
            f"[Identidad — {n} experiencias] "
            f"{character}{trend_note}{domain}{actions}"
        ).strip()

    def as_dict(self) -> dict:
        """Return the raw profile for API/dashboard use."""
        return dict(self._profile)

    # ── Convenience ──────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Wipe the identity profile (does NOT wipe memory)."""
        self._profile = {}
        self._save()
