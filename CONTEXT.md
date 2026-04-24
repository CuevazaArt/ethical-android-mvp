# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos V2 Core Minimal (Fase 16 COMPLETA)
- **Architecture:** `src/core/` → `src/server/` → `src/clients/` (zero legacy)
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-24 (V2.25)

## Fase α ✅ · Fase β ✅ · Fase γ ✅ · Fase δ ✅ · Fase 16 ✅

## Active block

**V2.26 — Fase 17: A definir con L0.**

## Closed blocks

| Block | Name | Status |
|-------|------|--------|
| V2.1 | Chat Terminal | ✅ |
| V2.2 | Ethical Perception | ✅ |
| V2.3 | Functional Memory | ✅ |
| V2.4 | Safety Gate | ✅ |
| V2.5 | WebSocket Chat | ✅ |
| V2.6 | Streaming | ✅ |
| V2.7 | Dashboard | ✅ |
| V2.8 | Nomad PWA | ✅ |
| V2.9 | Audio VAD | ✅ |
| V2.10 | STT→Chat pipeline | ✅ |
| V2.11 | Whisper STT server-side | ✅ |
| V2.12 | Vision frame processing | ✅ |
| V2.13 | Vision → Kernel context | ✅ |
| V2.14 | Nomad PWA HTTPS | ✅ |
| V2.15 | Identity Neuroplasticity | ✅ |
| V2.16 | Dashboard Identity Telemetry | ✅ |
| V2.17 | TF-IDF Semantic Recall + Adversarial Hardening R2 | ✅ |
| V2.18 | Latency & Performance Audit | ✅ |
| V2.19 | Dashboard TTFT + Integration Tests E2E | ✅ |
| V2.20 | Server Integration Tests + SyntaxError fix | ✅ |
| V2.21 | Identity Throttle (every 5 turns) | ✅ |
| V2.22 | Perception Hardening | ✅ |
| V2.23 | Nomad Latency Visualizer | ✅ |
| **Fase 16 — Estabilización V2** | | |
| V2.23 (P16) | Purge legacy (kernel_lobes, modules, kernel_components) | ✅ |
| V2.24 | Delete bridge, adversarial_suite V2 direct | ✅ |
| V2.25 | README V2, docs aligned, Phase 16 closed | ✅ |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,identity,vision,stt,status}.py` |
| Server | `src/server/app.py` |
| Nomad PWA | `src/clients/nomad_pwa/{index.html,app.js,media_engine.js,style.css,sw.js}` |
| CLI | `src/ethos_cli.py` |
| Entry | `src/main.py` (REPL) · `src/chat_server.py` (uvicorn) |
| Tests | `tests/core/` (91 tests) |
| Security | `scripts/eval/adversarial_suite.py` |
| Run | `python -m src.chat_server` or `uvicorn src.server.app:app --port 8765` |
| Chat | `http://localhost:8765/` |
| Dashboard | `http://localhost:8765/dashboard` |
| Nomad | `http://[LAN-IP]:8765/nomad` |

## System health (2026-04-24)

- **Tests:** 91/91 ✅
- **Legacy imports:** 0
- **Bridge:** ELIMINADO
- **Documentación:** Alineada con el código
- **Adversarial Suite:** 6/6 blocked · 10/10 legitimate pass (sin Ollama: keyword fallback activo)
