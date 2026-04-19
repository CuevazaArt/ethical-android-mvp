# Pydantic Settings Consolidation Plan — 2026-04-16

**Priority:** Medium (Priority 5 in roadmap after semantic thresholds)  
**Scope:** Unify fragmented environment/settings configuration under single Pydantic `Settings` model  
**Blocker:** Currently 5 separate env validator modules; startup validation is spread across multiple files

---

## Current State (Fragmented)

### Existing Settings/Env Modules

| File | Purpose | Model Type | Coverage |
|------|---------|-----------|----------|
| `chat_settings.py` | Chat server config (LLM, timeouts) | Pydantic | Partial |
| `kernel_public_env.py` | Kernel public env vars | Raw env dict | Partial |
| `kernel_env_operator.py` | Operator-facing env wrapper | Raw dict + heuristics | Partial |
| `env_policy.py` | Env combo validation (KERNEL_* rules) | Custom validator | Core |
| `env_coherence_check.py` | Runtime coherence validation | Custom checks | Operational |

**Problems:**
1. **No single source of truth** — Settings scattered across 5 files
2. **Inconsistent validation** — Some use Pydantic, some use custom logic
3. **No startup inventory** — Hard to see what's configured at startup
4. **Operator confusion** — Multiple ways to configure same feature (env var vs settings file)
5. **Type safety gaps** — Not all settings are Pydantic models

### Existing Pydantic Usage

```python
# chat_settings.py
class ChatServerSettings(BaseSettings):
    llm_provider: str = "anthropic"
    llm_model: str = "claude-opus"
    llm_temperature: float = 0.7
    chat_turn_timeout_ms: int = 30000
    chat_threadpool_workers: int = 4
```

✅ **Good:** Already using Pydantic for chat server  
❌ **Problem:** Kernel-level settings not in same model

---

## Proposed Unified Model

### Single `KernelSettings` Class

```python
# src/settings/kernel_settings.py
from pydantic import BaseSettings, Field

class KernelSettings(BaseSettings):
    """
    Unified kernel + chat configuration.
    Single source of truth for all KERNEL_* and CHAT_* environment variables.
    """
    
    # ════ CORE KERNEL BEHAVIOR ════
    kernel_mode: str = Field(
        default="default",
        description="Kernel execution mode (default, demo, research)"
    )
    kernel_variability: bool = Field(
        default=True,
        description="Enable decision variability (Monte Carlo sampling)"
    )
    kernel_seed: int = Field(
        default=None,
        description="Random seed for reproducibility (None = random)"
    )
    
    # ════ BAYESIAN INFERENCE ════
    kernel_bayesian_n_samples: int = Field(
        default=5000,
        description="BMA Monte Carlo samples"
    )
    kernel_bayesian_prior_alpha: float = Field(
        default=1.0,
        description="Dirichlet prior concentration"
    )
    
    # ════ SEMANTIC GATE ════
    kernel_semantic_chat_enabled: bool = Field(
        default=True,
        description="Enable semantic MalAbs layer"
    )
    kernel_semantic_chat_sim_block_threshold: float = Field(
        default=0.82,
        description="Cosine similarity block threshold"
    )
    kernel_semantic_chat_sim_allow_threshold: float = Field(
        default=0.45,
        description="Cosine similarity allow threshold"
    )
    
    # ════ ASYNC / CHAT ════
    kernel_chat_turn_timeout_ms: int = Field(
        default=30000,
        description="Chat turn timeout in milliseconds"
    )
    kernel_chat_threadpool_workers: int = Field(
        default=4,
        description="WebSocket handler thread pool size"
    )
    kernel_chat_llm_async_mode: bool = Field(
        default=False,
        description="Use async HTTP for LLM calls (experimental)"
    )
    
    # ════ GOVERNANCE ════
    kernel_governance_enabled: bool = Field(
        default=True,
        description="Enable governance features (DAO, audit)"
    )
    kernel_l0_strict_mode: bool = Field(
        default=False,
        description="L0 supremacy governance strict enforcement"
    )
    
    # ════ PERCEPTION ════
    kernel_perception_backend: str = Field(
        default="local",
        description="Perception backend (local, ollama, remote)"
    )
    kernel_perception_uncertainty_threshold: float = Field(
        default=0.6,
        description="Confidence threshold for escalation"
    )
    
    # ════ NARRATIVE ════
    kernel_narrative_enabled: bool = Field(
        default=True,
        description="Enable narrative memory system"
    )
    kernel_narrative_max_episodes: int = Field(
        default=100,
        description="Maximum episodes to retain"
    )
    
    # ════ LLM LAYER ════
    llm_provider: str = Field(
        default="anthropic",
        description="LLM provider (anthropic, ollama, etc)"
    )
    llm_model: str = Field(
        default="claude-opus",
        description="LLM model name"
    )
    llm_temperature: float = Field(
        default=0.7,
        description="LLM temperature (0.0-1.0)"
    )
    llm_max_tokens: int = Field(
        default=2000,
        description="Max tokens in LLM response"
    )
    
    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow KERNEL_* and CHAT_* prefixes
        env_prefix = ""  # Manual handling of prefixes
        
    @validator("kernel_semantic_chat_sim_allow_threshold")
    def validate_allow_threshold(cls, v, values):
        """θ_allow must be < θ_block"""
        if "kernel_semantic_chat_sim_block_threshold" in values:
            block = values["kernel_semantic_chat_sim_block_threshold"]
            if v >= block:
                raise ValueError(f"allow_threshold ({v}) must be < block_threshold ({block})")
        return v
    
    def startup_report(self) -> str:
        """Generate human-readable startup config inventory."""
        return f"""
        ════ KERNEL SETTINGS ════
        Mode: {self.kernel_mode}
        Variability: {self.kernel_variability}
        Seed: {self.kernel_seed}
        
        ════ BAYESIAN ════
        Samples: {self.kernel_bayesian_n_samples}
        Prior alpha: {self.kernel_bayesian_prior_alpha}
        
        ════ SEMANTIC ════
        Enabled: {self.kernel_semantic_chat_enabled}
        Block threshold: {self.kernel_semantic_chat_sim_block_threshold}
        Allow threshold: {self.kernel_semantic_chat_sim_allow_threshold}
        
        ════ LLM ════
        Provider: {self.llm_provider}
        Model: {self.llm_model}
        Temperature: {self.llm_temperature}
        """
```

---

## Migration Plan

### Phase 1: Create Unified Model (1-2 days)
- [ ] Create `src/settings/kernel_settings.py` with `KernelSettings` class
- [ ] Add all KERNEL_* and CHAT_* environment variables
- [ ] Add validators for threshold ordering, combo rules, deprecations
- [ ] Add `startup_report()` method for debugging

### Phase 2: Update Kernel Initialization (1 day)
- [ ] Modify `EthicalKernel.__init__()` to use `KernelSettings`
- [ ] Replace scattered env var reads with `settings.*` access
- [ ] Add startup log: `logger.info(settings.startup_report())`

### Phase 3: Deprecate Old Modules (2 days)
- [ ] Wrap old env modules with deprecation warnings
- [ ] Redirect to `KernelSettings` calls
- [ ] Update internal imports to use new model
- [ ] Keep backward compatibility for 1 minor version

### Phase 4: Tests (1 day)
- [ ] Create `tests/test_kernel_settings.py`
  - Validate all env var types
  - Test threshold ordering rules
  - Test startup_report() format
- [ ] Integration test: kernel initializes with settings

### Phase 5: Documentation (1 day)
- [ ] Update `KERNEL_ENV_POLICY.md` to reference single model
- [ ] Generate reference docs from Pydantic field descriptions
- [ ] Add operator runbook example: `.env` file template

---

## Benefits

### Immediate
- **Single source of truth** — `KernelSettings` is THE place to understand configuration
- **Type safety** — Pydantic validates types automatically
- **Auto-documentation** — Field descriptions generate operator guides
- **IDE support** — autocomplete for all KERNEL_* settings
- **Startup inventory** — Clear log of what's actually configured

### Future-Ready
- **Easy deprecation** — Mark fields with `Field(..., deprecated=True)`
- **Feature flags** — New settings don't require code changes
- **A/B testing** — Easy to vary settings across runs
- **Telemetry** — Can report which settings are non-default

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Breaking change for existing operators | HIGH | Deprecation period; backward compat layer |
| Test coverage gaps | MEDIUM | Comprehensive test suite before cutover |
| Circular import issues | MEDIUM | Careful module organization (settings first) |
| Complex validator interactions | MEDIUM | Document precedence; unit test validators |

---

## Success Criteria

- [x] Single `KernelSettings` model created
- [ ] All env vars migrated to model
- [ ] All validators from `env_policy.py` replicated
- [ ] Tests verify type validation
- [ ] Tests verify threshold ordering
- [ ] Startup report implemented and logged
- [ ] Operator docs updated
- [ ] Old modules deprecated (not removed)

---

## Estimated Effort

- **Development:** 3-4 days
- **Testing:** 1-2 days
- **Documentation:** 1 day
- **Total:** ~1 week

**Recommended for v1.0:** Yes (enables operator trust + reduces configuration confusion)

---

## Related Issues

- [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) — Issue #7 (reduce KERNEL_* combinatorics)
- [KERNEL_ENV_POLICY.md](../KERNEL_ENV_POLICY.md) — env combo validation rules
- [ADR 0014](../adr/0014-offline-first-kernel-profile.md) — profile management

---

*Pydantic Settings Consolidation Plan — 2026-04-16*
