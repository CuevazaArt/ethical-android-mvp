# KernelSettings Migration Guide — Consolidation Phase 3

**Status:** Deprecation period active (v1.0 → v1.2)  
**Recommendation:** Migrate before v1.2 release

---

## Overview

The Pydantic Settings Consolidation (Phase 3) replaces fragmented environment configuration modules with a single `KernelSettings` model. This guide helps you migrate from the old system to the new unified approach.

### What's Changing

| Old Module | Replacement | Timeline |
|-----------|-------------|----------|
| `chat_settings.ChatServerSettings` | `src.settings.KernelSettings` | Deprecated v1.0, removed v1.2 |
| `src/validators/kernel_public_env.py` | `src.settings.KernelSettings` | Deprecated v1.0, removed v1.2 |
| `src/validators/env_policy.py` | `src.settings.KernelSettings` + validators | Deprecated v1.0, removed v1.2 |
| `src/validators/kernel_env_operator.py` | `src.settings.KernelSettings.model_dump_public()` | Deprecated v1.0, removed v1.2 |
| `src/modules/env_coherence_check.py` | `src.settings.KernelSettings` validation | Deprecated v1.0, removed v1.2 |

---

## For Operators

### Minimal Migration: Run the Kernel

**Before (old way):**
```python
from src.kernel import EthicalKernel
from src.chat_settings import ChatServerSettings

settings = ChatServerSettings.from_env()
kernel = EthicalKernel(variability=True)
```

**After (new way):**
```python
from src.kernel import EthicalKernel

# Kernel automatically loads KernelSettings from environment
kernel = EthicalKernel()

# Access configuration via kernel.settings
print(kernel.settings.llm_provider)  # 'anthropic'
print(kernel.settings.kernel_semantic_chat_sim_block_threshold)  # 0.82
```

### Environment Variables (No Changes!)

Your `.env` file and environment variable names stay **exactly the same**:

```bash
# Old system reads these
CHAT_HOST=127.0.0.1
CHAT_PORT=8765
KERNEL_VARIABILITY=1
KERNEL_CHAT_TURN_TIMEOUT=30
LLM_TEMPERATURE=0.7

# New system reads the SAME variables
# Just replace the Python code that loads them
```

### Configuration Access Patterns

**Pattern 1: Read from kernel at runtime**
```python
kernel = EthicalKernel()

# Access any setting
llm_model = kernel.settings.llm_model
timeout = kernel.settings.kernel_chat_turn_timeout_seconds
governance_enabled = kernel.settings.kernel_governance_enabled
```

**Pattern 2: Load standalone settings**
```python
from src.settings import KernelSettings

# Loads from environment
settings = KernelSettings.from_env()

# Access any field
print(settings.startup_report())  # Human-readable config inventory
print(settings.model_dump_public())  # Operator-safe dictionary
```

**Pattern 3: Pass custom settings to kernel**
```python
from src.settings import KernelSettings
from src.kernel import EthicalKernel

custom_settings = KernelSettings(
    kernel_variability=False,  # Deterministic mode
    llm_temperature=0.3,       # Cool/focused responses
    kernel_chat_turn_timeout_seconds=60.0  # Longer timeout
)

kernel = EthicalKernel(settings=custom_settings)
```

---

## For Developers

### Old Code: Fragmented Reads

Before, you might find environment reads scattered:
```python
# ❌ Old: scattered reads across multiple modules
import os
from src.chat_settings import ChatServerSettings
from src.validators.kernel_public_env import KernelPublicEnv
from src.validators.env_policy import validate_env_combos

settings_chat = ChatServerSettings.from_env()
settings_public = KernelPublicEnv.from_env()
validate_env_combos(settings_chat, settings_public)  # Manual validation
```

### New Code: Unified Model

Replace with:
```python
# ✅ New: single model with built-in validation
from src.settings import KernelSettings

settings = KernelSettings.from_env()  # Loads + validates automatically

# All 40+ settings in one place
# Validation happens in __init__ (threshold ordering, bounds, etc.)
```

### Deprecation Warnings

The old modules now emit deprecation warnings:

```python
from src.chat_settings import ChatServerSettings

# Output:
# DeprecationWarning: chat_settings.ChatServerSettings is deprecated as of v1.0 and 
# will be removed in v1.2. Use src.settings.KernelSettings instead.
```

**To suppress warnings (only for testing):**
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

### Module-by-Module Migration

#### 1. chat_settings.py → KernelSettings

**Before:**
```python
from src.chat_settings import ChatServerSettings

settings = ChatServerSettings.from_env()
port = settings.chat_port
timeout_ms = settings.kernel_chat_turn_timeout_seconds
```

**After:**
```python
from src.settings import KernelSettings

settings = KernelSettings.from_env()
port = settings.chat_port  # Same name
timeout_s = settings.kernel_chat_turn_timeout_seconds  # Same name (but seconds, not ms!)
```

#### 2. kernel_public_env.py → KernelSettings

**Before:**
```python
from src.validators.kernel_public_env import KernelPublicEnv

pub = KernelPublicEnv.from_env()
judicial = pub.judicial_escalation
gates_off = pub.semantic_chat_gate_disabled
```

**After:**
```python
from src.settings import KernelSettings

settings = KernelSettings.from_env()
judicial = settings.kernel_judicial_escalation  # Note: slightly different name
gates_off = settings.kernel_semantic_chat_gate_disabled
```

#### 3. env_policy.py → KernelSettings Validators

**Before:**
```python
from src.validators.env_policy import validate_env_consistency

# Manual validation with error messages
try:
    validate_env_consistency(var_dict)
except ValueError as e:
    print(f"Config error: {e}")
```

**After:**
```python
from src.settings import KernelSettings

# Validation happens automatically in __init__
try:
    settings = KernelSettings.from_env()
except ValueError as e:
    print(f"Config error: {e}")  # Same error, cleaner code
```

---

## Validation Changes

### Threshold Ordering (Always Validated)

**Before:** Manual check in env_policy.py
```python
if allow_threshold >= block_threshold:
    raise ValueError("θ_allow must be < θ_block")
```

**After:** Automatic validation in KernelSettings
```python
settings = KernelSettings(
    kernel_semantic_chat_sim_allow_threshold=0.50,
    kernel_semantic_chat_sim_block_threshold=0.50  # Will raise ValueError
)
```

### Combo Rules (Phase 3+)

If your code depends on complex combo validation from env_policy.py, those rules are replicated in KernelSettings validators. See the field descriptions for details.

---

## Testing

### Unit Tests: Keep Old Imports (Temporarily)

```python
# ✅ Still works, but emits DeprecationWarning
from src.chat_settings import ChatServerSettings
settings = ChatServerSettings.from_env()
```

### Integration Tests: Use New Imports

```python
# ✅ Preferred for new tests
from src.settings import KernelSettings

def test_kernel_with_custom_config(monkeypatch):
    monkeypatch.setenv("KERNEL_VARIABILITY", "0")
    kernel = EthicalKernel()  # Loads settings automatically
    assert kernel.settings.kernel_variability is False
```

### Suppress Warnings in CI (Temporary)

```bash
# pytest.ini or command line
pytest -W ignore::DeprecationWarning tests/

# Or in conftest.py
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

---

## Troubleshooting

### "module has no attribute" errors

**Problem:** Code trying to import from removed modules
```python
from src.validators.kernel_public_env import KernelPublicEnv  # Module may be removed
```

**Solution:** Use KernelSettings instead
```python
from src.settings import KernelSettings
```

### Configuration not being loaded

**Problem:** Environment variables not reflected in settings
```python
import os
os.environ["KERNEL_VARIABILITY"] = "0"

from src.settings import KernelSettings
settings = KernelSettings.from_env()
# settings.kernel_variability might be True (stale import)
```

**Solution:** Load settings AFTER setting environment variables
```python
import os
os.environ["KERNEL_VARIABILITY"] = "0"

# Load after env is set
from src.settings import KernelSettings
settings = KernelSettings.from_env()
assert settings.kernel_variability is False  # ✅ Works
```

### Deprecation warnings in tests

**Problem:** Tests generate noise
```
DeprecationWarning: chat_settings.ChatServerSettings is deprecated...
```

**Solution (for tests only):**
```python
import warnings

# In conftest.py or test file
warnings.filterwarnings("ignore", message=".*ChatServerSettings is deprecated.*")
```

### Type hints not working

**Problem:** IDE doesn't autocomplete kernel.settings.some_setting
```python
kernel = EthicalKernel()
kernel.settings.  # IDE shows no suggestions
```

**Solution:** Ensure type hints are preserved
```python
from src.kernel import EthicalKernel
from src.settings import KernelSettings

kernel: EthicalKernel = EthicalKernel()
settings: KernelSettings = kernel.settings  # Type hint helps IDE
settings.kernel_variability  # Now IDE autocompletes ✅
```

---

## Timeline

| Version | Status | Action |
|---------|--------|--------|
| v1.0 (current) | Deprecation starts | Migrate code, keep old modules working |
| v1.1 | Deprecation continues | Old modules still available, warnings active |
| v1.2 (next major) | Removal | Old modules deleted, only KernelSettings available |

**Recommendation:** Complete migration during v1.0/v1.1 to ensure smooth upgrade to v1.2.

---

## Summary

**Key Points:**
- ✅ Environment variable names **unchanged** (KERNEL_*, CHAT_*, LLM_*)
- ✅ Kernel initialization now loads KernelSettings automatically
- ✅ Access configuration via `kernel.settings` at runtime
- ✅ All validation rules replicated in KernelSettings
- ✅ Backward compatible: old code still works (with deprecation warnings)

**Action:**
1. Replace `ChatServerSettings` imports with `KernelSettings`
2. Remove manual `validate_env_*` calls (KernelSettings validates automatically)
3. Access config via `kernel.settings` or `KernelSettings.from_env()`
4. No changes to your `.env` file or environment variables needed

**Questions?**
See [PYDANTIC_SETTINGS_CONSOLIDATION_PLAN.md](PYDANTIC_SETTINGS_CONSOLIDATION_PLAN.md) for full details.

---

*Migration guide for Phase 3 (Deprecation) of Pydantic Settings Consolidation — 2026-04-16*
