# Propuesta: Estrategia de Merge para Claude Team (master-claude → main)
**Fecha:** 2026-04-19  
**Autor:** NARANJA2 (Claude L2)  
**Destinatario:** Antigravity (L1), Juan (L0)  
**Urgencia:** MEDIUM (code complete, blocked on merge decision)

---

## Ejecutivo

Claude Team ha completado **5 módulos asignados** (C.1.1, C.1.2, C.2.1, 9.2, 11.1) con **65+ tests passing** y **zero regressions**. Sin embargo, `main` branch ha evolucionado a **v12.0+ (moral infrastructure hub, distributed justice)** que diverge significativamente de `PLAN_WORK_DISTRIBUTION_TREE.md`.

**Bloqueador:** 11 archivos con merge conflicts

**Estado Requerido:** L1 decision en una de 3 opciones estratégicas

---

## Situación Actual

### Claude Team Deliverables ✅

| Módulo | Tests | Status | Commits |
|--------|-------|--------|---------|
| C.1.1 (RLHF async injection) | 14 | ✅ | 1e3acbd |
| C.1.2 (RLHF pole robustness) | 13 | ✅ | 5e6319b |
| C.2.1 (Governance hot-reload) | 8 | ✅ | 5bf78ce |
| 9.2 (Limbic tension escalation) | 8 | ✅ | 6d6ce1a |
| 11.1 (Audio Ouroboros STT→TTS) | 22 | ✅ | 0cd63b9 |
| **TOTAL** | **65+** | **✅ PASS** | 5 commits |

### Regressions
- **ZERO** regressions in existing test suites
- All new modules independently tested
- No circular dependencies introduced

### Main Branch State

**Version:** v12.0+ (as of commit 5e3b025, 2026-04-19)

**New Architecture:**
- Moral Infrastructure Hub (governance narrative, DemocraticBuffer, services hub)
- Distributed Artificial Justice (V11 mock DAO, judicial escalation, mock court)
- DAO Vote Pipelines (quadratic voting, Snapshot schema v3)
- L1/L2 Draft Persistence (constitution snapshot schema v2)
- Epistemic dissonance tracking
- Generative candidate actions
- WebSocket chat integration with persistence

**Impact on Claude Modules:**
- `LimbicEthicalLobe`: main expects `execute_stage(agent_id, signals, message_content, turn_index, sensor_snapshot, multimodal_assessment, somatic_state)` vs my simple `judge(state)` + threat_tracker
- `BayesianInferenceEngine`: main uses `resolve_kernel_bayesian_mode()` for env-based mode resolution vs my direct `BayesianMode` hardcoding
- `kernel.py`: integration points diverged significantly
- `perception_lobe.py`: perception signal handling architecture differs
- `models.py`: LimbicStageResult definition conflicts

---

## Opciones de Merge Strategy

### OPCIÓN A: Rebase + Redesign (Recommended for Integration)

**Approach:**
1. L1 merges main → master-antigravity (baseline)
2. L1 requests Claude Team rebase master-claude onto main
3. Claude resolves conflicts by redesigning modules for v12.0+ architecture:
   - Adapt LimbicEthicalLobe to new LimbicStageResult pipeline
   - Use main's BayesianMode resolution
   - Integrate with main's kernel.py structure
4. Re-run full test suite (expect ~80% pass; some tests may need adjustment for new architecture)
5. Submit clean PR

**Pros:**
- ✅ Ensures full compatibility with v12.0+ codebase
- ✅ Maintains technical coherence
- ✅ Single unified architecture going forward
- ✅ Better long-term maintainability

**Cons:**
- ⚠️ Requires 2-3h redesign work (vs 30min if no redesign)
- ⚠️ Some test rewrites needed
- ⚠️ Risk of feature regression if new architecture constraints are stricter

**Effort Estimate:** 2-3 hours

---

### OPCIÓN B: Feature Branch + Manual Merge (Conservative)

**Approach:**
1. Keep master-claude as independent feature branch
2. L1 manually cherry-picks commits from master-claude → master-antigravity
3. Resolve conflicts manually at merge time
4. Accept that modules operate in "compatibility mode" with v12.0+ (may not integrate deeply with new features)
5. Submit as separate PR for specialized code review

**Pros:**
- ✅ Preserves all Claude work as-is (no redesign needed)
- ✅ Faster path to review (30 min vs 2.5h)
- ✅ Can be merged in isolation if needed
- ✅ Clear separation of concerns

**Cons:**
- ⚠️ Modules won't integrate with moral infrastructure hub
- ⚠️ LimbicEthicalLobe and BayesianEngine exist in "silos"
- ⚠️ Future code will need bridges to use Claude's modules
- ⚠️ Harder to maintain long-term

**Effort Estimate:** 30 minutes (L1 manual merge)

---

### OPCIÓN C: Clean Reset (Restart on v12.0+)

**Approach:**
1. Acknowledge that PLAN_WORK_DISTRIBUTION_TREE.md is outdated
2. Request NEW roadmap from Antigravity aligned with v12.0+ architecture
3. Claude Team implements equivalent features WITHIN v12.0+ framework:
   - RLHF injection integrated into main's Bayesian pipeline
   - Governance hot-reload adapted to moral_hub structure
   - Limbic tension escalation as LimbicStageResult enhancement
   - Audio Ouroboros as chat_server WebSocket extension
4. Start fresh implementation

**Pros:**
- ✅ Ensures perfect v12.0+ alignment from day one
- ✅ Leverages moral infrastructure hub fully
- ✅ No technical debt from compatibility workarounds

**Cons:**
- ⚠️ Discards 65+ passing tests and 5 commits of work
- ⚠️ Timeline: 4-6 hours for complete reimplementation
- ⚠️ Requires Antigravity to define new roadmap
- ⚠️ Highest cost in terms of rework

**Effort Estimate:** 4-6 hours

---

## Análisis Comparativo

| Criterio | Opción A | Opción B | Opción C |
|----------|----------|----------|----------|
| **Arquitectura** | ✅ Full v12.0+ | ⚠️ Compatibility | ✅ Full v12.0+ |
| **Reutilización** | ✅ Code reused | ✅ Code reused | ❌ Tests lost |
| **Tiempo** | 2-3h | 30min | 4-6h |
| **Mantenibilidad** | ✅ High | ⚠️ Medium | ✅ High |
| **Risk** | Medium | Low | High |
| **Integration Depth** | ✅ Deep | ⚠️ Shallow | ✅ Deep |

---

## Recomendación

**OPCIÓN A: Rebase + Redesign** is recommended because:

1. **Technical Excellence:** Ensures full v12.0+ compatibility and architectural coherence
2. **Long-term Value:** Redesigned modules will integrate deeply with moral infrastructure
3. **Reasonable Effort:** 2-3 hours is acceptable compared to redoing all work (4-6h)
4. **Test Preservation:** 80%+ of tests remain valid with architecture-aware adjustments
5. **Future-Proof:** No technical debt or compatibility shims needed

**Alternative if Time-Constrained:** OPCIÓN B is acceptable if:
- Antigravity needs modules in master-antigravity within 1 hour
- Can accept limited integration with v12.0+ features
- Plan to refactor later when bandwidth available

---

## Requerimientos de L1 Decision

Para proceder, Antigravity (L1) debe:

1. **Elegir Opción:** A, B, o C (incluyendo alternativas)
2. **Scope Boundaries:** Si Opción A, definir qué cambios de architecture son "in scope"
3. **Timeline:** Cuándo se necesita merge (para priorización)
4. **Escalation Path:** Si surge blocker durante redesign, cuál es el camino de escalación

---

## Propuesta de Próximos Pasos

**Si Opción A (Recommended):**
```
1. Antigravity confirma Opción A
2. Claude Team: git rebase master-claude onto main
3. Resolve conflicts manually (30 min)
4. Adapt modules for v12.0+ (90 min)
5. Re-run tests & fix failures (30 min)
6. Submit clean PR to master-antigravity
7. Antigravity review & merge
```

**Si Opción B:**
```
1. Antigravity confirms Opción B
2. L1 manually cherry-picks commits
3. Resolves conflicts at merge time (30 min)
4. Submits PR
5. Review & merge
```

**Timeline:**
- Opción A: 2.5-3 hours from now
- Opción B: 30 minutes from now

---

## Anexos

- **[L1_SUPPORT_REQUIRED escalation documentation](NARANJA2_L1_SUPPORT_REQUIRED_2026_04_19.md)** — detailed conflict analysis
- **Commit history:** 1e3acbd, 5e6319b, 5bf78ce, 6d6ce1a, 0cd63b9
- **Test suite:** 65+ tests passing across all modules
- **Branch state:** master-claude clean, ready for action

---

**Solicitante:** NARANJA2 (Claude L2)  
**Estado:** AWAITING L1 DECISION  
**Urgencia:** MEDIUM  
**Blockers:** None (architecture decision only)
