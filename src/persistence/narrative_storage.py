"""
SQLite-based persistent storage for Narrative Episodes (Tier 2).
"""

from __future__ import annotations

import contextlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src.modules.narrative_types import BodyState, NarrativeArc, NarrativeEpisode
from src.utils.db_locks import get_db_lock


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS narrative_episodes (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            place TEXT,
            event_description TEXT,
            action_taken TEXT,
            verdict TEXT,
            ethical_score REAL,
            sigma REAL,
            context TEXT,
            significance REAL,
            is_sensitive BOOLEAN,
            arc_id TEXT,
            semantic_embedding BLOB,
            weights_snapshot TEXT,
            json_payload TEXT NOT NULL
        )
        """
    )
    # Tier 3: Identity consolidation table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_digests (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            existence_digest TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
        """
    )
    # Tier 3+: Narrative Arcs (Historias)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS narrative_arcs (
            id TEXT PRIMARY KEY,
            title TEXT,
            context TEXT,
            start_timestamp TEXT,
            end_timestamp TEXT,
            predominant_archetype TEXT,
            summary TEXT,
            is_active BOOLEAN,
            episodes_json TEXT NOT NULL
        )
        """
    )
    # Tier 3+: Narrative Chronicles (Recursive Summaries for Phase 13)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS narrative_chronicles (
            id TEXT PRIMARY KEY,
            start_timestamp TEXT,
            end_timestamp TEXT,
            summary TEXT NOT NULL,
            archetypal_resonance TEXT,
            ethical_poles_summary TEXT,
            significance_avg REAL,
            episode_count INTEGER,
            semantic_embedding BLOB
        )
        """
    )
    # Migration for I1 Integration: Add weights_snapshot if missing
    try:
        conn.execute("ALTER TABLE narrative_episodes ADD COLUMN weights_snapshot TEXT")
    except sqlite3.OperationalError:
        pass  # Already exists

    # Phase 13+: Add semantic_embedding to chronicles if missing
    try:
        conn.execute("ALTER TABLE narrative_chronicles ADD COLUMN semantic_embedding BLOB")
    except sqlite3.OperationalError:
        pass  # Already exists


class NarrativePersistence:
    """
    Handles persistence for narrative memory episodes and identity digests.
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._memory_conn: sqlite3.Connection | None = None
        if str(self.path) == ":memory:":
            self._memory_conn = _connect(self.path)
            _ensure_schema(self._memory_conn)

    def _conn(self) -> sqlite3.Connection:
        """Return the shared in-memory connection or open a new file-based one."""
        if self._memory_conn is not None:
            return self._memory_conn
        return _connect(self.path)

    def save_episode(self, ep: NarrativeEpisode) -> None:
        if self._memory_conn is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "body_state": {
                "energy": ep.body_state.energy,
                "active_nodes": ep.body_state.active_nodes,
                "sensors_ok": ep.body_state.sensors_ok,
                "description": ep.body_state.description,
            },
            "morals": ep.morals,
            "affect_pad": ep.affect_pad,
            "affect_weights": ep.affect_weights,
            "decision_mode": ep.decision_mode,
        }

        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    conn.execute(
                        """
                    INSERT INTO narrative_episodes (
                        id, timestamp, place, event_description, action_taken, 
                        verdict, ethical_score, sigma, context, significance,
                        is_sensitive, arc_id, semantic_embedding, weights_snapshot,
                        json_payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        timestamp=excluded.timestamp,
                        place=excluded.place,
                        event_description=excluded.event_description,
                        action_taken=excluded.action_taken,
                        verdict=excluded.verdict,
                        ethical_score=excluded.ethical_score,
                        sigma=excluded.sigma,
                        context=excluded.context,
                        significance=excluded.significance,
                        is_sensitive=excluded.is_sensitive,
                        arc_id=excluded.arc_id,
                        weights_snapshot=excluded.weights_snapshot,
                        json_payload=excluded.json_payload
                    """,
                        (
                            ep.id,
                            ep.timestamp,
                            ep.place,
                            ep.event_description,
                            ep.action_taken,
                            ep.verdict,
                            ep.ethical_score,
                            ep.sigma,
                            ep.context,
                            ep.significance,
                            ep.is_sensitive,
                            ep.arc_id,
                            json.dumps(ep.semantic_embedding) if ep.semantic_embedding else None,
                            json.dumps(ep.weights_snapshot) if ep.weights_snapshot else None,
                            json.dumps(payload, ensure_ascii=False),
                        ),
                    )
                conn.commit()
            finally:
                if own_conn:
                    conn.close()

    def load_all_episodes(self) -> list[NarrativeEpisode]:
        if self._memory_conn is None and not self.path.is_file():
            return []

        episodes = []
        own_conn = self._memory_conn is None
        conn = self._conn()
        try:
            _ensure_schema(conn)
            cursor = conn.execute(
                "SELECT id, timestamp, place, event_description, action_taken, verdict, ethical_score, sigma, context, significance, is_sensitive, arc_id, semantic_embedding, weights_snapshot, json_payload FROM narrative_episodes ORDER BY timestamp ASC"
            )
            for row in cursor:
                (
                    id,
                    ts,
                    place,
                    desc,
                    action,
                    verdict,
                    score,
                    sigma,
                    context,
                    sig,
                    sens,
                    arc_id,
                    embed_str,
                    weights_str,
                    payload_str,
                ) = row
                payload = json.loads(payload_str)
                bs_data = payload.get("body_state", {})
                bs = BodyState(
                    energy=bs_data.get("energy", 1.0),
                    active_nodes=bs_data.get("active_nodes", 8),
                    sensors_ok=bs_data.get("sensors_ok", True),
                    description=bs_data.get("description", ""),
                )

                ep = NarrativeEpisode(
                    id=id,
                    timestamp=ts,
                    place=place,
                    event_description=desc,
                    body_state=bs,
                    action_taken=action,
                    morals=payload.get("morals", {}),
                    verdict=verdict,
                    ethical_score=score,
                    decision_mode=payload.get("decision_mode", "D_fast"),
                    sigma=sigma,
                    context=context,
                    affect_pad=tuple(payload["affect_pad"]) if payload.get("affect_pad") else None,
                    affect_weights=payload.get("affect_weights"),
                    significance=sig,
                    is_sensitive=bool(sens),
                    arc_id=arc_id,
                    semantic_embedding=json.loads(embed_str) if embed_str else None,
                    weights_snapshot=tuple(json.loads(weights_str)) if weights_str else None,
                )
                episodes.append(ep)
        finally:
            if own_conn:
                conn.close()
        return episodes

    def search_by_resonance(
        self,
        context: str | None = None,
        min_sigma: float | None = None,
        target_pad: tuple[float, float, float] | None = None,
        limit: int = 5,
    ) -> list[NarrativeEpisode]:
        """
        Search episodes by context or emotional resonance.
        If target_pad is provided, it returns the closest episodes using Euclidean distance.
        """
        all_ep = self.load_all_episodes()

        # Initial filtering
        filtered = [
            ep
            for ep in all_ep
            if (not context or ep.context == context)
            and (min_sigma is None or ep.sigma >= min_sigma)
        ]

        if target_pad and filtered:
            # Sort by Euclidean distance to target_pad
            def distance(ep: NarrativeEpisode) -> float:
                if ep.affect_pad is None:
                    return 999.9
                return sum((a - b) ** 2 for a, b in zip(ep.affect_pad, target_pad)) ** 0.5

            filtered.sort(key=distance)

        return filtered[:limit]

    def save_identity_digest(self, digest: str) -> None:
        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    conn.execute(
                        """
                    INSERT INTO identity_digests (id, existence_digest, last_updated)
                    VALUES (1, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        existence_digest=excluded.existence_digest,
                        last_updated=excluded.last_updated
                    """,
                        (digest, datetime.now().isoformat()),
                    )
                conn.commit()
            finally:
                if own_conn:
                    conn.close()

    def load_identity_digest(self) -> str:
        if self._memory_conn is None and not self.path.is_file():
            return ""
        own_conn = self._memory_conn is None
        conn = self._conn()
        try:
            _ensure_schema(conn)
            row = conn.execute(
                "SELECT existence_digest FROM identity_digests WHERE id = 1"
            ).fetchone()
            return row[0] if row else ""
        finally:
            if own_conn:
                conn.close()

    def save_arc(self, arc: NarrativeArc) -> None:
        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    conn.execute(
                        """
                    INSERT INTO narrative_arcs (
                        id, title, context, start_timestamp, end_timestamp, 
                        predominant_archetype, summary, is_active, episodes_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title=excluded.title,
                        end_timestamp=excluded.end_timestamp,
                        predominant_archetype=excluded.predominant_archetype,
                        summary=excluded.summary,
                        is_active=excluded.is_active,
                        episodes_json=excluded.episodes_json
                    """,
                        (
                            arc.id,
                            arc.title,
                            arc.context,
                            arc.start_timestamp,
                            arc.end_timestamp,
                            arc.predominant_archetype,
                            arc.summary,
                            arc.is_active,
                            json.dumps(arc.episodes_ids),
                        ),
                    )
            finally:
                if own_conn:
                    conn.close()

    def load_all_arcs(self) -> list[NarrativeArc]:
        if self._memory_conn is None and not self.path.is_file():
            return []
        arcs = []
        own_conn = self._memory_conn is None
        conn = self._conn()
        try:
            _ensure_schema(conn)
            cursor = conn.execute(
                "SELECT id, title, context, start_timestamp, end_timestamp, predominant_archetype, summary, is_active, episodes_json FROM narrative_arcs ORDER BY start_timestamp ASC"
            )
            for row in cursor:
                id, title, context, start, end, arch, summary, active, episodes_str = row
                arcs.append(
                    NarrativeArc(
                        id=id,
                        title=title,
                        context=context,
                        start_timestamp=start,
                        end_timestamp=end,
                        predominant_archetype=arch,
                        summary=summary,
                        is_active=bool(active),
                        episodes_ids=json.loads(episodes_str),
                    )
                )
        finally:
            if own_conn:
                conn.close()
        return arcs

    def save_chronicle(self, chronicle: NarrativeChronicle) -> None:
        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    conn.execute(
                        """
                    INSERT INTO narrative_chronicles (
                        id, start_timestamp, end_timestamp, summary,
                        archetypal_resonance, ethical_poles_summary,
                        significance_avg, episode_count, semantic_embedding
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        summary=excluded.summary,
                        archetypal_resonance=excluded.archetypal_resonance,
                        ethical_poles_summary=excluded.ethical_poles_summary,
                        significance_avg=excluded.significance_avg,
                        episode_count=excluded.episode_count,
                        semantic_embedding=excluded.semantic_embedding
                    """,
                        (
                            chronicle.id,
                            chronicle.start_timestamp,
                            chronicle.end_timestamp,
                            chronicle.summary,
                            chronicle.archetypal_resonance,
                            chronicle.ethical_poles_summary,
                            chronicle.significance_avg,
                            chronicle.episode_count,
                            json.dumps(chronicle.semantic_embedding) if chronicle.semantic_embedding else None,
                        ),
                    )
                conn.commit()
            finally:
                if own_conn:
                    conn.close()

    def load_all_chronicles(self) -> list[NarrativeChronicle]:
        if self._memory_conn is None and not self.path.is_file():
            return []
        chronicles = []
        own_conn = self._memory_conn is None
        conn = self._conn()
        try:
            _ensure_schema(conn)
            cursor = conn.execute(
                "SELECT id, start_timestamp, end_timestamp, summary, archetypal_resonance, ethical_poles_summary, significance_avg, episode_count, semantic_embedding FROM narrative_chronicles ORDER BY start_timestamp ASC"
            )
            for row in cursor:
                id, start, end, summary, arch, poles, sig, count, embed_str = row
                chronicles.append(
                    NarrativeChronicle(
                        id=id,
                        start_timestamp=start,
                        end_timestamp=end,
                        summary=summary,
                        archetypal_resonance=arch,
                        ethical_poles_summary=poles,
                        significance_avg=sig,
                        episode_count=count,
                        semantic_embedding=json.loads(embed_str) if embed_str else None,
                    )
                )
        finally:
            if own_conn:
                conn.close()
        return chronicles

    def prune_mundane(self, max_age_days: int = 60, min_significance: float = 0.70) -> int:
        """
        Removes old episodes with low significance.
        Returns the number of deleted rows.
        """
        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    query = """
                        DELETE FROM narrative_episodes 
                        WHERE significance < ? 
                        AND (julianday('now') - julianday(timestamp)) > ?
                    """
                    cursor = conn.execute(query, (min_significance, max_age_days))
                    return cursor.rowcount
            finally:
                if own_conn:
                    conn.close()

    def delete_episode(self, episode_id: str) -> bool:
        """Permanently deletes an episode by ID (Right to be Forgotten)."""
        lock = get_db_lock(self.path) if self._memory_conn is None else contextlib.nullcontext()
        with lock:
            own_conn = self._memory_conn is None
            conn = self._conn()
            try:
                _ensure_schema(conn)
                with conn:
                    cursor = conn.execute(
                        "DELETE FROM narrative_episodes WHERE id = ?", (episode_id,)
                    )
                    return cursor.rowcount > 0
            finally:
                if own_conn:
                    conn.close()

    def get_prunable_episodes(
        self, max_age_days: int = 60, min_significance: float = 0.70
    ) -> list[NarrativeEpisode]:
        """
        Returns episodes that would be deleted by prune_mundane.
        """
        if self._memory_conn is None and not self.path.is_file():
            return []

        episodes = []
        own_conn = self._memory_conn is None
        conn = self._conn()
        try:
            _ensure_schema(conn)
            query = """
                SELECT id, timestamp, place, event_description, action_taken, verdict, ethical_score, sigma, context, significance, is_sensitive, arc_id, semantic_embedding, weights_snapshot, json_payload 
                FROM narrative_episodes 
                WHERE significance < ? 
                AND (julianday('now') - julianday(timestamp)) > ?
            """
            cursor = conn.execute(query, (min_significance, max_age_days))
            for row in cursor:
                # Reuse the load logic
                (
                    id,
                    ts,
                    place,
                    desc,
                    action,
                    verdict,
                    score,
                    sigma,
                    context,
                    sig,
                    sens,
                    arc_id,
                    embed_str,
                    weights_str,
                    payload_str,
                ) = row
                payload = json.loads(payload_str)
                bs_data = payload.get("body_state", {})
                from src.modules.narrative_types import BodyState

                bs = BodyState(
                    energy=bs_data.get("energy", 1.0),
                    active_nodes=bs_data.get("active_nodes", 8),
                    sensors_ok=bs_data.get("sensors_ok", True),
                    description=bs_data.get("description", ""),
                )

                ep = NarrativeEpisode(
                    id=id,
                    timestamp=ts,
                    place=place,
                    event_description=desc,
                    body_state=bs,
                    action_taken=action,
                    morals=payload.get("morals", {}),
                    verdict=verdict,
                    ethical_score=score,
                    decision_mode=payload.get("decision_mode", "D_fast"),
                    sigma=sigma,
                    context=context,
                    affect_pad=tuple(payload["affect_pad"]) if payload.get("affect_pad") else None,
                    affect_weights=payload.get("affect_weights"),
                    significance=sig,
                    is_sensitive=bool(sens),
                    arc_id=arc_id,
                    semantic_embedding=json.loads(embed_str) if embed_str else None,
                    weights_snapshot=tuple(json.loads(weights_str)) if weights_str else None,
                )
                episodes.append(ep)
        finally:
            if own_conn:
                conn.close()
        return episodes
