# Deprecation Roadmap — Scheduled flag retirements

**Purpose:** Record timeline for removing or consolidating `KERNEL_*` flags as the API matures. Prevents silent breakage and gives operators clear migration paths.

**Policy:** Deprecated flags must (1) have a replacement path documented, (2) be announced in `CHANGELOG.md`, (3) log warnings when used, (4) remain functional for at least one minor version before removal.

---

## Deprecation Lifecycle

```
1. Proposal: decision recorded here with rationale
   ↓
2. Announcement: CHANGELOG + release notes mention deprecation + replacement
   ↓
3. Warning Phase: code logs WARN when flag is used
   ↓
4. Support Period: 2–4 releases (time varies by impact); code continues to work
   ↓
5. Removal: flag is deleted in major version; migration guide published
```

---

## Current Deprecations (None Scheduled Yet)

| Flag | Status | Replacement | Rationale | Target Removal |
|------|--------|-------------|-----------|-----------------|
| *(none)* | — | — | — | — |

---

## Proposed Future Deprecations (Candidates)

These are **candidate** flags under consideration for deprecation. No timeline assigned yet.

### 1. `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` → `KERNEL_MIXTURE_ADAPTIVE_WEIGHTS`

**Rationale:** "Bayesian" is a misnomer (not full posterior inference); renamed to clarify semantics.  
**Replacement:** `KERNEL_MIXTURE_ADAPTIVE_WEIGHTS` (same behavior, clearer name).  
**Migration:** Set both during transition period; code ignores old flag if new one is present.  
**Impact:** Low (rarely used in production; mostly lab).  
**Status:** Candidate; awaiting Issue #1 resolution (Bayesian naming consolidation).

---

### 2. `KERNEL_PERCEPTION_BACKEND_POLICY` (partial consolidation)

**Rationale:** Split into `KERNEL_LLM_PERCEPTION_POLICY` + `KERNEL_LLM_COMMUNICATION_POLICY` for clarity.  
**Replacement:** Two separate flags (perception and communication have different fallback needs).  
**Migration:** `KERNEL_PERCEPTION_BACKEND_POLICY=fast_fail` → set both new flags to `fast_fail`.  
**Impact:** Medium (affects operator config; downstream dashboards if named).  
**Status:** Candidate; requires [ADR 0010](../adr/0010-llm-policy-split.md) (not yet proposed).

---

### 3. `KERNEL_SWARM_STUB` → `KERNEL_FLEET_STUB` (retirement pending rename)

**Rationale:** "Swarm" vocabulary retired in V2.159. Stub has not evolved; peer-to-peer multi-instance features are out of scope for MVP.
**Replacement:** `KERNEL_FLEET_STUB` (neutral naming; same semantics).
**Migration:** Operators can rename or delete from configs.
**Impact:** Low (never used; always explicitly opt-in for lab).
**Status:** Candidate; awaiting Phase 4+ roadmap (2–3 quarters out).

---

### 4. `KERNEL_CHAT_TURN_TIMEOUT` (rename → `KERNEL_CHAT_TURN_DEADLINE_SECONDS`)

**Rationale:** "Deadline" is clearer than "timeout" (absolute vs relative semantics).  
**Replacement:** `KERNEL_CHAT_TURN_DEADLINE_SECONDS`.  
**Migration:** Simple rename; no behavioral change.  
**Impact:** Low (config-only; no code changes needed).  
**Status:** Candidate; nice-to-have for April–May sprint.

---

## Archive: Previously Deprecated (Reference)

| Flag | Removed in | Replacement | Status |
|------|-----------|-------------|--------|
| *(none yet)* | — | — | archived |

---

## Operator Migration Guide (Template)

When a deprecation is announced, operators should:

1. **Check CHANGELOG.md** for the announcement and timeline.
2. **Update config** (e.g., environment file, helm values, docker-compose env).
3. **Test thoroughly** in staging; log WARN messages in this version.
4. **Plan upgrade** before removal deadline.

Example (hypothetical):

```bash
# Old (deprecated in v6.0; removed in v7.0)
export KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS=1

# New (replacement in v6.0+)
export KERNEL_MIXTURE_ADAPTIVE_WEIGHTS=1
```

---

## Policy for Adding New Flags

- **Required:** document in [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) **before** merge.
- **Required:** add corresponding test in `tests/test_env_policy.py`.
- **Optional but encouraged:** announce in `CHANGELOG.md` if user-facing.
- **No flag without a clear "why":** avoid proliferation.

---

## See Also

- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) — current flag reference.
- [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) — operator guide.
- [CHANGELOG.md](../../CHANGELOG.md) — version history and announcements.
- [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md) — roadmap context.

---

*Document version:* April 2026 (no deprecations scheduled yet). Update when a flag is proposed for removal.
