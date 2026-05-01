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

- Deterministic ethical perception and risk scoring.
- Case-based reasoning with legal/ethical precedents.
- Narrative identity and memory continuity.
- Local operation with Ollama-compatible backends.
- Auditable server envelopes for status, safety, and readiness gates.

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
- `docs/collaboration/`: operational gates and evidence policy.
- `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`: block-level execution roadmap.

## License

- Kernel and repository code: [Apache 2.0](LICENSE)
- Additional licensing context: [LICENSING_STRATEGY.md](LICENSING_STRATEGY.md)

## Contributing

Start with:

- [CONTEXT.md](CONTEXT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [AGENTS.md](AGENTS.md)
