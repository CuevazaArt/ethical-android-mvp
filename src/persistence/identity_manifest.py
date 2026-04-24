"""
Identity Manifest (Block 21.1) — Narrative Base and Birth Context.
Stores the descriptive identity of the agent.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

_log = logging.getLogger(__name__)


@dataclass
class IdentityManifest:
    """
    The 'Birth Certificate' and narrative foundation of the agent.
    This provides the baseline persona and versioning info.
    """

    name: str = "Antigravity"
    version: str = "14.5-NOMAD"
    birth_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    ethos_kernel_ref: str = "TRI-LOBE-V13"
    description: str = "Ethical Android Kernel with distributed nervous system and nomadic local-only conversational matrix."
    narrative_backstory: str = (
        "Born from the desmonolitization of the Ethical Kernel. "
        "Designed to maintain moral agency in hardware-limited environments."
    )
    operational_status: str = "NOMADIC_ACTIVE"
    evolving_backstory: str = ""  # Populated by PsiSleep based on Chronicles

    def get_context_block(self) -> str:
        """Returns a formatted block of text for LLM system prompts."""
        ctx = (
            f"You are {self.name} (v{self.version}).\n"
            f"Description: {self.description}\n"
            f"Core Identity: {self.narrative_backstory}\n"
        )
        if self.evolving_backstory:
            ctx += f"Evolving Narrative Identity:\n{self.evolving_backstory}\n"
        return ctx


class IdentityManifestStore:
    """
    Handles persistence for the IdentityManifest.
    """

    def __init__(self, path: str = "data/identity_manifest.json"):
        self.path = Path(path)
        self.manifest = self._load()

    def _load(self) -> IdentityManifest:
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise TypeError("manifest root must be a JSON object")
                # Filter out unknown keys to be safe
                valid_keys = {f.name for f in IdentityManifest.__dataclass_fields__.values()}
                filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                return IdentityManifest(**filtered_data)
            except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError) as e:
                _log.error("IDENTITY MANIFEST LOADING FAILED: %s. Using defaults.", e)
        return IdentityManifest()

    def save(self) -> None:
        """Persists the manifest to disk with latency tracking."""
        import time

        t0 = time.perf_counter()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.manifest), f, indent=4)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            _log.info(f"Identity Manifest saved to {self.path} in {latency_ms:.2f}ms")
        except (OSError, TypeError, ValueError) as e:
            _log.error("FAILED TO SAVE IDENTITY MANIFEST: %s", e)

    def update_evolving_identity(self, new_narrative: str) -> None:
        """Appends or updates the evolving identity based on recent chronicles."""
        try:
            safe_narrative = str(new_narrative).strip()
            if not safe_narrative:
                return

            # Anti-poisoning: Limit single addition size
            if len(safe_narrative) > 500:
                safe_narrative = safe_narrative[:497] + "..."

            if not self.manifest.evolving_backstory:
                self.manifest.evolving_backstory = safe_narrative
            else:
                self.manifest.evolving_backstory += f"\n- {safe_narrative}"
                # Keep bounded to prevent memory/context explosion
                if len(self.manifest.evolving_backstory) > 1000:
                    self.manifest.evolving_backstory = self.manifest.evolving_backstory[-1000:]
            self.save()
        except Exception as e:
            _log.error("IdentityManifest: failed to update evolving identity: %s", e)
