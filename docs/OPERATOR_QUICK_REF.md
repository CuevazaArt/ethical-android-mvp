# Operator quick reference — `KERNEL_*` families

**Canonical detail:** [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) · **profiles:** [`src/runtime_profiles.py`](../src/runtime_profiles.py) · **chat keys:** [`src/chat_server.py`](../src/chat_server.py) docstring / README WebSocket section.

| Family | Prefix / examples | Typical role |
|--------|---------------------|--------------|
| Chat JSON telemetry | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Include/omit WebSocket fields (UX only). |
| Persistence / handoff | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk snapshots, encryption, conduct export. |
| Input / epistemics | `KERNEL_LIGHTHOUSE_KB_PATH`, `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | Lighthouse KB path; reality JSON in chat. |
| Perception / sensors | `KERNEL_SENSOR_FIXTURE`, `KERNEL_SENSOR_PRESET`, `KERNEL_MULTIMODAL_*` | Situated v8 snapshot merge; multimodal thresholds. |
| Governance / hub | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Hub, drafts, judicial, integrity audit. |
| LLM / variability | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = JSON candidates in perception) | Backends and generative candidates. |
| **Bayesian episodic** | `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` | When `1`, mixture weights are nudged from recent episode scores (same context). Default `0`. |

**Rule:** if a combination is not a **named profile** and not covered by a **test**, treat it as experimental ([`ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md)).
