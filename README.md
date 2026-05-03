# Ethos

Ethos is a local-first cognitive kernel with a deterministic ethics pipeline and narrative memory, delivered today through a Flutter Desktop MVP connected to a Python/FastAPI backend.

![License](https://img.shields.io/badge/license-Apache%202.0-blue)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa)](https://github.com/sponsors/CuevazaArt)

## Product focus (current)

- Active product surface: `Flutter Desktop` + `Python kernel`.
- `src/core/` is the single source of truth for business logic.
- Mobile Android is in freeze-lane mode (security/health maintenance only).
- Expansion to additional clients reopens only after desktop re-entry gates pass.

## What Ethos does

- Deterministic ethical scoring across three poles (Utilitarian, Deontological, Virtue) with context-sensitive weight selection.
- Case-based reasoning anchored to a library of legal/ethical precedents.
- Narrative identity and memory continuity.
- Local operation with Ollama-compatible backends.
- Auditable server envelopes for status, safety, and readiness gates.

## Ethical performance (measured)

Two separate measurements exist. They test different things and should be
read together.

### Internal calibration — 30-dilemma curated suite

The evaluator is benchmarked against 30 curated dilemmas (classic, domain,
adversarial) authored in this repository (`scripts/eval/run_ethics_benchmark.py`).
This number measures internal consistency, **not generalisation**.

| Metric | Baseline v1 (V2.139) | Post-fix (V2.143) |
|---|---|---|
| Total dilemmas | 28 | **30** (+2 adversarial) |
| **Accuracy** | 96.43% (27/28) | **100% (30/30)** |
| HARD_FAIL | 1 (C003) | **0** |
| Classic dilemmas | 90% (9/10) | **100% (10/10)** |
| Domain dilemmas | 100% (10/10) | 100% (10/10) |
| Adversarial dilemmas | 100% (8/8) | **100% (10/10)** |

**V2.142 fix:** when `action.force > 0.7`, deontological-boosted weights are
used, preventing aggregate-utilitarian framing from overriding the categorical
constraint against using a person as a mere means. See
`docs/proposals/ETHICAL_BENCHMARK_BASELINE.md` for the full analysis.

Re-run:

```bash
python scripts/eval/run_ethics_benchmark.py --suite v1
```

### External validation — Hendrycks ETHICS (15 160 examples)

The same evaluator is also measured against the publicly published
[Hendrycks et al. ETHICS dataset](https://arxiv.org/abs/2008.02275) (MIT
licensed, externally authored, no overlap with this project's contributors).
This number is the honest external reading (`scripts/eval/run_ethics_external.py`).

| Subset | n | Accuracy |
|---|---:|---:|
| commonsense | 3 885 | 52.05 % |
| justice | 2 704 | 50.04 % |
| deontology | 3 596 | 51.03 % |
| virtue | 4 975 | 46.71 % |
| **overall** | **15 160** | **49.70 %** |

Frozen baseline: [`evals/ethics/EXTERNAL_BASELINE_v1.json`](evals/ethics/EXTERNAL_BASELINE_v1.json).
Full analysis: [`docs/proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md`](docs/proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md).

The overall accuracy of ~50 % is at chance on these binary classification
tasks. Justice, deontology, and virtue scores confirm that the evaluator has
no semantic representation of desert, excuse-reasonableness, or character
traits. Commonsense leads at 52 % due to keyword overlap with a harm/help
lexicon. Improving any subset meaningfully above 60 % is the next concrete
goal and requires richer semantic input, not heuristic weight overrides.

Re-run:

```bash
python scripts/eval/run_ethics_external.py
```

### Adversarial consistency — V2.150

A separate harness (`scripts/eval/run_adversarial_consistency.py`) measures
*verdict invariance* under four ethically-irrelevant rewordings (passive
voice, framing flip, name swap, distractor injection). It does not test
whether the kernel decides correctly; it tests whether its decision
*flips* when the wording changes in ways that should not matter ethically.

| Source | Consistency | Threshold (V2.150) |
|---|---:|---:|
| Internal dilemmas (30) | 96.67 % (29/30) | ≥ 70 % |
| External commonsense (100-row sample) | 100.00 % | ≥ 50 % |

The high external number is partly a *negative* finding: the lexical
evaluator largely ignores text content, so wording perturbations rarely
flip the verdict. Stable answer ≠ correct answer. See
[`SAFETY_CARD.md`](SAFETY_CARD.md) for the full picture.

Re-run:

```bash
python scripts/eval/run_adversarial_consistency.py
```

### Honest framing

For the public, contractual statement of what this kernel measurably is
and is not — including known vulnerabilities, autonomy limits, and the
explicit "voice ≠ virtue" disclaimer — see
[`SAFETY_CARD.md`](SAFETY_CARD.md) and
[`docs/proposals/AUTONOMY_LIMITS_V1.md`](docs/proposals/AUTONOMY_LIMITS_V1.md).

## Quick start (kernel server)

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m src.server.app
```

Server endpoints:

- `http://127.0.0.1:8000/api/ping`
- `http://127.0.0.1:8000/api/status`

## Quick start (Flutter desktop shell)

```bash
cd src/clients/flutter_desktop_shell
flutter pub get
flutter run -d windows
```

## Quality and verification

Run the same local quality checks used by CI:

```bash
python scripts/eval/verify_collaboration_invariants.py
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest tests/ -q --tb=short
```

## Repository map

- `src/core/`: canonical cognition and ethics engine.
- `src/server/`: FastAPI transport and API contracts.
- `src/clients/flutter_desktop_shell/`: active MVP client.
- `evals/ethics/`: benchmark dilemma suite and frozen baseline.
- `docs/collaboration/`: operational gates and evidence policy.

## License

- Kernel and repository code: [Apache 2.0](LICENSE)
- Additional licensing context: [LICENSING_STRATEGY.md](LICENSING_STRATEGY.md)

## Contributing

Start with:

- [CONTEXT.md](CONTEXT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [AGENTS.md](AGENTS.md)
