# Runtime profiles — operator table

**Apply at startup:** `ETHOS_RUNTIME_PROFILE=<name>` (see [`src/runtime_profiles.py`](../../src/runtime_profiles.py)). Explicit environment variables **override** profile defaults per key. **`GET /health`** returns `runtime_profile` when set.

| Profile | Summary | Risk / ops notes |
|---------|---------|------------------|
| `baseline` | Minimal flags; CI regression surface. | Default bind `127.0.0.1` unless you set `CHAT_HOST`. |
| `judicial_demo` | Judicial escalation + mock court JSON. | Advisory only; not legal process. |
| `hub_dao_demo` | Constitution HTTP + DAO WebSocket vote/list. | Mock governance; LAN + `KERNEL_API_DOCS` review [SECURITY.md](../../SECURITY.md). |
| `nomad_demo` | Nomad migration simulation + optional DAO audit line. | Lab stub; no real P2P. |
| `reality_lighthouse_demo` | Lighthouse KB + `reality_verification` in chat. | Run from **repo root** (fixture path relative). |
| `lan_mobile_thin_client` | Bind `0.0.0.0:8765` + semantic MalAbs (hash fallback). | **LAN exposure** — trusted network only; semantic tier adds latency. |
| `operational_trust` | Stoic WebSocket UX (omit homeostasis, monologue, digest). | UX only; ethics unchanged. |
| `lan_operational` | LAN bind + stoic UX + semantic gate + hash fallback. | Same LAN + embedding tier caveats as above. |
| `moral_hub_extended` | Full V12 hub stack + semantic gate + hash fallback. | Broad attack surface if exposed; read [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md). |
| `situated_v8_lan_demo` | v8 sensors (fixture+preset) + vitality/multimodal + LAN + semantic gate. | Requires fixture file; LAN bind. |
| `perception_hardening_lab` | Light-risk tier, cross-check, uncertainty→delib, parse fail-local. | Tuning may increase `D_delib` rate; monitor [metrics](../../src/observability/metrics.py). |
| `phase2_event_bus_lab` | In-process `KernelEventBus` (`kernel.decision` / `kernel.episode_registered`). | Handlers must stay fast; see [ADR 0006](../adr/0006-phase2-core-boundary-and-event-bus.md). |
| `untrusted_chat_input` | Semantic MalAbs on + hash fallback only. | Compose with LAN profile for full demo; weaker than live embeddings. |
| `lexical_malabs_only` | Forces `KERNEL_SEMANTIC_CHAT_GATE=0`. | Paraphrase bypass risk higher; airgap / latency trade-off. |

## Related

- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) · [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) · [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) · [TRANSPARENCY_AND_LIMITS.md](../TRANSPARENCY_AND_LIMITS.md)
