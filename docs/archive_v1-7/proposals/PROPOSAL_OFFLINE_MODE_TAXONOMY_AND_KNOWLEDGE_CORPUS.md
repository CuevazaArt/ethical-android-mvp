# Proposal — Offline mode taxonomy, resource priority, and curated knowledge corpus

This note specifies **design intent** for full offline operation of Ethos Kernel–based runtimes: classification of offline states, separation of the **L0 constitutional buffer** from a **versioned offline knowledge pack**, resource and energy policy, and sync when connectivity returns. It does not replace MalAbs, the existing [`PreloadedBuffer`](../../src/modules/buffer.py), or ADRs; it extends the product model for community implementation and review.

## Motivation

Contributors track **“Full offline mode (5 layers of autonomy)”** as pending ([`CONTRIBUTING.md`](../../CONTRIBUTING.md)). Today, `PreloadedBuffer` holds **immutable foundational principles** and activation protocols—not encyclopedic or operational reference material. A separate, **curated, integrity-checked corpus** is required so local models can **ground** responses under partition **without bypassing** MalAbs or L0 constraints (see [`conduct_guide_export.py`](../../src/modules/conduct_guide_export.py): do not bypass MalAbs or the preloaded buffer for speed).

## 1. Offline taxonomy

The runtime should expose an explicit **`OfflineContext`** (conceptual contract) so policy, logging, and UX differ by situation:

| Class | Description | Examples | Design implication |
|-------|-------------|----------|---------------------|
| **Voluntary** | Operator or policy disables or restricts network use. | Privacy mode, scheduled radio-off, air-gapped demo. | Predictable windows; proactive sync before transition; less “surprise” degradation. |
| **Transient / degraded link** | Short-term loss or severe degradation of connectivity. | Tunnel, underground rail, RF shadow, congestion. | Short horizon; queue-and-hold governance events; standard MalAbs paths if local corpus is intact. |
| **Local structural** | On-device link or power path fault. | Antenna, modem, RF subsystem, charging path hardware. | May be **long**; assume **no** remote reconciliation until repair; emphasize energy and mission degradation rules. |
| **Systemic / external** | Large-scale outage or hostile RF environment. | Regional blackout, disaster, jamming. | Maximum reliance on **local corpus**, maps, and emergency directory; secondary missions shrink; audit marks outputs as *provisional* where appropriate. |

**Detection inputs (non-exhaustive):** link-layer health (timeouts, loss, RTT), geofencing hints for known dead zones, explicit operator intent, and hardware/BMS signals for energy and charging.

## 2. Two structural pillars (do not conflate)

### 2.1 L0 — `PreloadedBuffer` (existing)

- **Role:** Hard constitution—principles and protocols not modified by learning or DAO vote ([`buffer.py`](../../src/modules/buffer.py)).
- **MalAbs alignment:** MalAbs and downstream gates continue to treat this as the **normative floor** for harmful or disallowed content.

### 2.2 Offline knowledge pack (new product layer; implementation TBD)

- **Role:** **Read-mostly reference** for the local LLM and planners: human-rights summaries, jurisdiction-aware legal/regulatory digests, first-aid and daily-life science **at lay level**, contingency manuals (curated excerpts), basic sociology, quick-reference ethics, **general-knowledge digest** (e.g. compressed encyclopedic summaries), **offline emergency numbers**, **local maps and POIs** (hospitals, police, workshops, banks where legally and operationally appropriate), and **operator-approved contacts** (e.g. guardians)—plus any other modules approved by policy.
- **Immutability semantics:** **Immutable for the duration of an offline window**, or **updated only via signed, curated manifests** when online—not rewritten at runtime by the model. This preserves trust in “what the pack said” during an incident.
- **MalAbs alignment:** The pack is **consultation and RAG grounding**, not a bypass. Retrieval must not substitute for MalAbs blocks; optional similarity checks can flag attempts to cite corpus to justify harmful acts (defense in depth).

**Naming (suggested):** `OfflineKnowledgePack` or environment-driven paths to **module bundles** (each module: version, region, content hash).

## 3. Corpus modules (suggested packaging)

| Module | Purpose | Staleness |
|--------|---------|-----------|
| Rights and legal frame | Support `legality`, dignity, escalation to legitimate authorities. | High sensitivity—version and jurisdiction metadata required. |
| Biology / sustenance / everyday physics | Support `compassion`, `no_harm` at non-expert level; **not** a substitute for professional medical or rescue services. | Periodic refresh when online. |
| Contingency manuals | Fire, evacuation, hazardous conditions—**short, curated** excerpts to limit hallucination surface. | Operator-reviewed updates. |
| Sociology / ethics quick reference | Tone, mediation heuristics, bias awareness. | Lower criticality than safety modules. |
| General culture digest | Conversational grounding when cloud KB is unavailable. | Lowest priority for refresh. |
| Local directory and POI | Emergencies, services, navigation. | **Region- and time-bounded**; show “as of” dates in operator tooling. |
| Approved contacts | Family/guardian reach-out—**only** if policy and law allow; encrypt at rest. | Strict access control. |

## 4. Resource and energy hierarchy

When offline, **computational and electrical budget** should follow a fixed priority order:

1. **Ethical core survival** — Minimum CPU/memory/state to run MalAbs-relevant paths, L0 consultation, and critical state persistence (below this, the platform is not ethically trustworthy).
2. **Primary service directives** — Mission objectives **within** L0 and operator constraints.
3. **Safety-related sensing** — Minimal perception needed to avoid harm (e.g. mobility safety).
4. **Mobility and actuators** — Only if budget allows and the offline plan authorizes.
5. **Expensive LLM use** — **First class to degrade** (smaller model, shorter context, template-heavy replies) while keeping L0 + pack consultation available where possible.

**Energy floor:** Define an **absolute reserve** (SOC or joule budget) for **ordered shutdown**, **checkpoint/consistency**, and **optional emergency beacon**—**never** draining to a state where the ethical stack cannot run or persist without corruption. **Recharging / energy resupply** must be an **explicit planning objective** when entering offline mode (see §5), not an afterthought.

Integrate with existing vitality hooks ([`chat_server.py`](../../src/chat_server.py) docstring: `KERNEL_VITALITY_*`, `KERNEL_CHAT_INCLUDE_VITALITY`) so offline planning and JSON surfaces can reflect **degraded modes** honestly.

## 5. Entry into offline mode — planning

On transition to offline (especially **voluntary** and **structural**), the runtime should:

1. **Classify** offline class and **estimate horizon** (unknown allowed).
2. **Snapshot** pack versions, map epochs, and legal/contact freshness; mark stale data.
3. **Build a degraded mission plan:** ordered tasks by impact and **energy cost**; include **mandatory recharge milestones** before crossing low-energy thresholds.
4. **Enqueue sync** for governance/audit/feedback events for when the link returns (aligns with partitioned-hub design in [`ROADMAP_PRACTICAL_PHASES.md`](../ROADMAP_PRACTICAL_PHASES.md) and future reconciliation specs).
5. **Expose operator-facing state:** mode class, reserve policy, next recharge waypoint (if any).

## 6. Reconnection and updates

- **Signed deltas or manifests** per module; reject or quarantine updates that fail hash/signature checks.
- **Conflict policy** for law, maps, contacts: e.g. curated remote wins, or operator confirmation—must be **one** explicit rule per deployment.
- **Audit:** Log which pack **version** was active during the offline interval for post-incident review and jurisdictional traceability.

## 7. Relation to existing code

| Artifact | Relation |
|----------|----------|
| [`PreloadedBuffer`](../../src/modules/buffer.py) | Unchanged in role; L0 only. |
| [`moral_hub.py`](../../src/modules/moral_hub.py) | L0 export for transparency; pack is separate from L0/L1/L2 hub articles. |
| [`reality_verification.py`](../../src/modules/reality_verification.py) | Precedent for **immutable local JSON** used as evidence—not a bypass. |
| [`existential_serialization.py`](../../src/modules/existential_serialization.py) | Offline **transfer** bundle; pack is a **stationary** curated store. |
| Vitality / checkpoints | Energy floor and persistence should integrate with offline planning. |

## 8. Implementation phasing (suggested)

1. **Contract:** `OfflineContext` + enums; logging and health JSON fields.
2. **Pack loader:** versioned modules, hash verification, region metadata.
3. **RAG path:** retrieve-only over pack chunks under MalAbs and L0 ordering.
4. **Planner hooks:** energy milestones + mission degradation rules.
5. **Sync client:** signed update channel and audit log of versions used offline.

## 9. Open decisions (for ADR or follow-up proposals)

- Exact **cryptographic profile** for pack signing (keys, rotation, air-gap updates).
- **Minimum ethical stack** definition when SOC is critically low (hibernation vs last-resort behaviors).
- **Multi-jurisdiction** packs on one device (split vs single active region).

## Canonical references

- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — language policy; pending “Full offline mode”.
- [`docs/ROADMAP_PRACTICAL_PHASES.md`](../ROADMAP_PRACTICAL_PHASES.md) — phased engineering roadmap.
- [`AGENTS.md`](../../AGENTS.md) — contributor orientation.

---

*Branch context: community workstream **`cursor-dellware/offline-mode-knowledge-proposal`** (local workspace DellWare, developed with Cursor); intended for eventual merge to `main` via PR.*
