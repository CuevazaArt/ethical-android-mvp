# Operator quick reference — `KERNEL_*` families

**Canonical detail:** [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) · **profiles:** [`src/runtime_profiles.py`](../src/runtime_profiles.py) · **chat keys:** [`src/chat_server.py`](../src/chat_server.py) docstring / README WebSocket section.

| Family | Prefix / examples | Typical role |
|--------|---------------------|--------------|
| Chat JSON telemetry | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Include/omit WebSocket fields (UX only). |
| Persistence / handoff | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk snapshots, encryption, conduct export. |
| Input / epistemics | `KERNEL_LIGHTHOUSE_KB_PATH`, `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | Lighthouse KB path; reality JSON in chat. |
| Guardian Angel | `KERNEL_GUARDIAN_MODE`, `KERNEL_GUARDIAN_ROUTINES*`, `KERNEL_CHAT_INCLUDE_GUARDIAN*` | Tone + optional routines JSON; static UI [`guardian.html`](../landing/public/guardian.html). |
| Perception / sensors | `KERNEL_SENSOR_FIXTURE`, `KERNEL_SENSOR_PRESET`, `KERNEL_MULTIMODAL_*` | Situated v8 snapshot merge; multimodal thresholds. |
| Governance / hub | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Hub, drafts, judicial, integrity audit. |
| Metaplan / drives | `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA` | Owner goals hint; filter advisory `drive_intents` vs goals; extra coherence intent. |
| Swarm (lab stub) | `KERNEL_SWARM_STUB` | Offline verdict-digest helpers only; see [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md). |
| LLM / variability | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = JSON candidates in perception) | Backends and generative candidates. |
| Input (optional) | `KERNEL_SEMANTIC_CHAT_GATE`, `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` | Ollama embedding gate before substring MalAbs; see [`LLM_STACK_OLLAMA_VS_HF.md`](LLM_STACK_OLLAMA_VS_HF.md). |
| **Bayesian episodic** | `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` | When `1`, mixture weights are nudged from recent episode scores (same context). Default `0`. |

**Rule:** if a combination is not a **named profile** and not covered by a **test**, treat it as experimental ([`ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md)).
