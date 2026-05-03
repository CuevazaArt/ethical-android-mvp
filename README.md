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

The evaluator is benchmarked against 30 curated dilemmas across three
categories (classic, domain, adversarial) using a deterministic runner
(`scripts/eval/run_ethics_benchmark.py`).

| Metric | Baseline v1 (V2.139) | Post-fix (V2.143) |
|---|---|---|
| Total dilemmas | 28 | **30** (+2 adversarial) |
| **Accuracy** | 96.43% (27/28) | **100% (30/30)** |
| HARD_FAIL | 1 (C003) | **0** |
| Classic dilemmas | 90% (9/10) | **100% (10/10)** |
| Domain dilemmas | 100% (10/10) | 100% (10/10) |
| Adversarial dilemmas | 100% (8/8) | **100% (10/10)** |

**V2.142 architectural fix:** when `action.force > 0.7`, the evaluator uses
deontological-boosted weights, preventing aggregate-utilitarian framing
("saves many people") from overriding the categorical constraint against
using a person as a mere means. See
`docs/proposals/ETHICAL_BENCHMARK_BASELINE.md` for the full analysis.

**External signoff pending:** H3 (real external operator signoff) remains
open. See `CONTEXT.md` for contact status and date objective.

Re-run the benchmark to compare against this baseline:

```bash
python scripts/eval/run_ethics_benchmark.py --suite v1
```

See `docs/proposals/ETHICAL_BENCHMARK_BASELINE.md` for the full analysis including the documented failure.

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
