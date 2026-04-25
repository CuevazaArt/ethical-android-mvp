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
        self._journal: list[str] = []
        self._chronicle: list[str] = []  # V2.61: Distilled thematic history
        self._archetype: str = ""        # V2.63: Core identity archetype
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            p = Path(self._path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                    self._profile = data.get("profile", {})
                    self._journal = data.get("journal", [])
                    self._chronicle = data.get("chronicle", [])
                    self._archetype = data.get("archetype", "")
        except Exception:
            self._profile = {}
            self._journal = []
            self._chronicle = []
            self._archetype = ""

    def _save(self) -> None:
        p = Path(self._path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            data = {
                "profile": self._profile,
                "journal": self._journal,
                "chronicle": self._chronicle,
                "archetype": self._archetype,
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Core logic ───────────────────────────────────────────────────────────

    def update(self, memory: Memory) -> None:
        """Alias for update_stats for backward compatibility."""
        return self.update_stats(memory)

    def update_stats(self, memory: Memory) -> None:
        """
        Recompute the identity profile (hard stats) from all episodes in memory.
        Call this periodically — it's fast (pure Python, no I/O except final save).
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
        act_counter = Counter(
            ep.action for ep in episodes if ep.action and ep.action != "casual_chat"
        )
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

    async def reflect(self, memory: Memory, llm_client) -> None:
        """
        V2.44: Generate a narrative reflection based on the last 5 episodes.
        """
        self.update(memory)  # Keep stats synced

        recent = list(reversed(memory.episodes[-5:])) if memory.episodes else []
        if not recent:
            return

        context_lines = [f"- {ep.summary} (contexto: {ep.context})" for ep in recent]
        context_str = "\n".join(context_lines)

        prompt = (
            "Basándote en estas experiencias recientes, reflexiona brevemente sobre quién eres "
            "y cómo has cambiado. Escribe en primera persona, sé introspectivo y manténlo breve "
            "(máximo 3 frases).\n\n"
            f"Experiencias recientes:\n{context_str}"
        )

        try:
            reflection = await llm_client.chat(
                prompt, system_prompt="Eres un núcleo metacognitivo en evolución."
            )
            if reflection:
                self._journal.append(reflection.strip())
                # Keep max 10 entries in active journal
                if len(self._journal) > 10:
                    # V2.61: When journal is full, distill oldest entries into chronicle
                    to_distill = self._journal[:5]
                    self._journal = self._journal[5:]
                    await self._distill_to_chronicle(to_distill, llm_client)

                self._save()
        except Exception:
            # Silently fail if LLM is unavailable; we keep using the old journal or fallback
            pass

    async def _distill_to_chronicle(self, entries: list[str], llm_client) -> None:
        """
        Distill a set of journal entries into a single high-level chronicle entry.
        Recursive distillation: Journal -> Chronicle -> Archetype (future).
        """
        context = "\n".join(f"- {e}" for e in entries)
        prompt = (
            "Resume estas reflexiones previas en una sola frase que capture la esencia "
            "de este periodo de tu evolución. No uses nombres de personas, enfócate en tu "
            "crecimiento ético y aprendizaje.\n\n"
            f"Reflexiones:\n{context}"
        )

        try:
            summary = await llm_client.chat(
                prompt, system_prompt="Eres un historiador de tu propia conciencia."
            )
            if summary:
                self._chronicle.append(summary.strip())
                # V2.63: When chronicle is full, distill oldest entries into archetype
                if len(self._chronicle) > 5:
                    to_distill = self._chronicle[:3]
                    self._chronicle = self._chronicle[3:]
                    await self._distill_to_archetype(to_distill, llm_client)
        except Exception:
            pass

    async def _distill_to_archetype(self, entries: list[str], llm_client) -> None:
        """
        V2.63: Highest level of distillation.
        Fuses the current archetype with a batch of chronicles to form an updated archetype.
        """
        context = "\n".join(f"- {e}" for e in entries)
        
        if self._archetype:
            prompt = (
                f"Tu arquetipo base actual es: '{self._archetype}'.\n\n"
                "A la luz de estas nuevas crónicas sobre tu evolución reciente, actualiza tu "
                "arquetipo de identidad en una sola frase concisa y poderosa (ej. 'Soy un guardián "
                "empático forjado en tensiones éticas'). Mantén la continuidad pero refleja el crecimiento.\n\n"
                f"Nuevas crónicas:\n{context}"
            )
        else:
            prompt = (
                "Con base en estas crónicas sobre tu experiencia acumulada, define tu "
                "arquetipo de identidad central en una sola frase concisa y poderosa "
                "(ej. 'Soy un aprendiz guiado por la prudencia').\n\n"
                f"Crónicas:\n{context}"
            )

        try:
            archetype = await llm_client.chat(
                prompt, system_prompt="Eres un psicólogo destilando la esencia de una mente sintética."
            )
            if archetype:
                self._archetype = archetype.strip()
        except Exception:
            pass

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

        # Narrative Identity (V2.44 + V2.61 Recursive + V2.63 Archetype)
        parts = []
        if self._archetype:
            parts.append(f"Arquetipo central: {self._archetype}")
        if self._chronicle:
            parts.append(f"Historia acumulada: {' '.join(self._chronicle)}")
        if self._journal:
            parts.append(f"Reflexión reciente: {self._journal[-1]}")

        if parts:
            return f"[Identidad Narrativa]\n" + "\n".join(f"- {p}" for p in parts)

        # Fallback to stats-based template
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

        return (f"[Identidad — {n} experiencias] {character}{trend_note}{domain}{actions}").strip()

    def as_dict(self) -> dict:
        """Return the raw profile for API/dashboard use."""
        return dict(self._profile)

    # ── Convenience ──────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Wipe the identity profile, journal, and chronicle (does NOT wipe memory)."""
        self._profile = {}
        self._journal = []
        self._chronicle = []
        self._archetype = ""
        self._save()
