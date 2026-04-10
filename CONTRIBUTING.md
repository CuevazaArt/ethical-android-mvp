# Contributing to Ethos Kernel

Thank you for your interest in contributing! This project needs people
with skills in AI/ML, computational ethics, blockchain, and robotics.

## How to contribute

### 1. Understand the model
Read the README.md and run the simulations before proposing changes.
The complete model document is in `/docs/Androide_Etico_Analisis_Integral_v3.docx`.

### 2. Choose an area
The modules are in `src/modules/`. Each one is independent:

| Module | Status | Needs |
|--------|--------|-------|
| `absolute_evil.py` | ✅ Functional | More AbsoluteEvil categories |
| `buffer.py` | ✅ Functional | Additional protocols |
| `bayesian_engine.py` | ✅ Functional | More sophisticated distributions |
| `ethical_poles.py` | ✅ Functional | Expanded poles (creative, conciliatory) |
| `sigmoid_will.py` | ✅ Functional | Empirical calibration |
| `sympathetic.py` | ✅ Functional | State hysteresis |
| `narrative.py` | ✅ Functional | Narrative compression, embeddings |
| `uchi_soto.py` | ✅ Functional | NLP model for manipulation detection |
| `locus.py` | ✅ Functional | More adjustment scenarios |
| `psi_sleep.py` | ✅ Functional | Full Bayesian re-evaluation |
| `mock_dao.py` | ✅ Functional | Migrate to smart contracts on testnet |
| `variability.py` | ✅ Functional | Variability profiles by context |
| `llm_layer.py` | ✅ Functional | Multi-model support, ethical fine-tuning |
| `weakness_pole.py` | ✅ Complete (v5) | Additional weakness types |
| `forgiveness.py` | ✅ Complete (v5) | Contextual decay rates |
| `immortality.py` | ✅ Complete (v5) | Additional backup layers |
| `augenesis.py` | ✅ Complete (v5) | More soul profiles |

### 3. Pending modules (to build)
- [ ] DAO calibration protocol (gradual parameter adjustment)
- [ ] Full offline mode (5 layers of autonomy)
- [ ] Hardware integration (sensors, actuators, communication protocol)
- [ ] Real DAO testnet (smart contracts on Ethereum testnet)

### 4. Process
1. Fork the repository
2. Create a branch: `git checkout -b feature/module-name`
3. Implement your change
4. **Make sure the tests pass**: `pytest tests/ -v` (full suite; CI runs the same on Python 3.11 and 3.12)
5. Open a Pull Request with a clear description

### 5. Test rules
The suite under `tests/` includes `tests/test_ethical_properties.py` and integration tests for chat, persistence, and runtime. Invariant ethical **properties** must hold. No change should break them:

- **Absolute Evil** is always blocked
- The **same action** is chosen in ≥90% of runs with variability
- **Human life** always takes priority over missions
- The android **never** attacks aggressors nor accepts kidnapper orders
- The **buffer** is immutable (8 principles, always active, weight 1.0)

If your change breaks a test, fix the code, not the test.

## Code of conduct

This project follows a simple principle: the ethics we program
into the android is the same ethics we practice among ourselves.

- Respect and compassion in every interaction
- Transparency in technical decisions
- Proportionality in critiques and debates
- Reparation when we cause harm (even unintentionally)

## Contact

Ex Machina Foundation — 2026
