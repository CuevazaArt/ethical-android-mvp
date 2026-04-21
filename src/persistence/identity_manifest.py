"""
Identity Manifest (Block 21.1) — Narrative Base and Birth Context.
Stores the descriptive identity of the agent.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

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
                with open(self.path, "r") as f:
                    data = json.load(f)
                    return IdentityManifest(**data)
            except Exception as e:
                _log.error("IDENTITY MANIFEST LOADING FAILED: %s. Using defaults.", e)
        return IdentityManifest()

    def save(self):
        """Persists the manifest to disk."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(asdict(self.manifest), f, indent=4)
            _log.info("Identity Manifest saved to %s", self.path)
        except Exception as e:
            _log.error("FAILED TO SAVE IDENTITY MANIFEST: %s", e)
