# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos V2 Core Minimal (Fase 17 COMPLETA)
- **Architecture:** `src/core/` → `src/server/` (zero legacy)
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-25 (V2.60 — `v22.3.3-field-tested`)

## Fase α ✅ · Fase β ✅ · Fase γ ✅ · Fase δ ✅ · Fase 16 ✅ · Fase 17 ✅

## Active block

**NEXT PHASE — Post-field-test development.**
V2.60 multimodal stabilization complete. Voice capture, vision, TTS, and WebSocket pipeline field-tested on Android hardware. PWA install validated as production-viable UX.

## Closed blocks

| Block | Name | Status |
|-------|------|--------|
| V2.40 | Perception Classifier (Sin LLM, 0ms) | ✅ |
| V2.41 | Case-Based Ethics (CBR Precedents) | ✅ |
| V2.42 | Single-Call Pipeline (Hardening) | ✅ |
| V2.43 | Sentence Embeddings (Memoria Semántica) | ✅ |
| V2.44 | Narrative Identity (LLM Journal Reflections) | ✅ |
| V2.45 | Nomad PWA Ethics HUD (Metadata stream) | ✅ |
| V2.46 | Precedents Expansion (36 rich cases) | ✅ |
| V2.47 | GPU Docker Orchestration (NVIDIA + Ollama) | ✅ |
| V2.48 | LLM Native Multi-turn & Crash Fixes | ✅ |
| V2.49 | Neural TTS (Voz propia para Ethos con edge-tts) | ✅ |
| V2.50 | Sensory Expansion — Autonomous vision triggers | ✅ |
| V2.51 | Thalamic Gate — Wake word protection against background noise | ✅ |
| V2.52 | Limbic System — Emotional TTS and Visual Resonance | ✅ |
| V2.53 | Acoustic Echo Shield — Ignore STT while playing audio | ✅ |
| V2.54 | Cognitive Proprioception — STT semantic echo cancellation & Preemption | ✅ |
| V2.55 | Temporal Multimodal Fusion — Audio & Video context sync | ✅ |
| V2.56 | Status Telemetry Hardening (Boy Scout) | ✅ |
| V2.57 | SensoryBuffer WebSocket Integration — Continuous fusion loop | ✅ |
| V2.58 | Speech-Triggered Immediate Fusion — Zero-delay audio response | ✅ |
| V2.59 | Sensory-Context Perception — Multimodal pattern recognition | ✅ |
| V2.60 | Audio Feedback Suppression — ScriptProcessor removed, SR text rescue, phantom turn kill | ✅ FIELD-TESTED |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,identity,vision,stt,tts,status,precedents}.py` |
| Server | `src/server/app.py` |
| CLI | `src/ethos_cli.py` |
| Entry | `src/main.py` (REPL) · `src/chat_server.py` (uvicorn) |
| Tests | `tests/core/` (165 tests) |
| Security | `scripts/eval/adversarial_suite.py` |
| Deploy | `Dockerfile.gpu` · `docker-compose.gpu.yml` · `scripts/docker_entrypoint.sh` |
| Run | `python -m src.chat_server` or `uvicorn src.server.app:app --port 8000` |
| Run GPU | `docker compose -f docker-compose.gpu.yml up --build` |
| Chat | `http://localhost:8000/` |
| Dashboard | `http://localhost:8000/dashboard` |
| Nomad | `https://[LAN-IP]:8443/nomad` |

## System health (2026-04-25)

- **Tests:** 165/165 ✅
- **Legacy imports:** 0
- **Perception:** Determinista (Sin LLM, latencia <1ms)
- **Ethics:** Basada en precedentes (CBR, 36 casos)
- **Memory:** Híbrida (Semantic Embeddings + TF-IDF fallback)
- **Identity:** Reflexiva (Narrative Journal + Stats)
- **Pipeline:** Single-Call Hardened (Background reflection, Early signaling)
- **PWA HUD:** Contexto ético en tiempo real (metadata event)
- **Adversarial Suite:** 6/6 blocked · 10/10 legitimate pass
- **GPU Deploy:** Docker + NVIDIA Container Toolkit + Ollama sidecar ready
- **Field Test:** Android PWA voice+vision confirmed (v22.3.3-field-tested)

## Known hardware limitations (field-tested)

- **Old Android SoC:** Camera and mic alternate (shared media pipeline). Cannot coexist simultaneously.
- **Mitigation:** SpeechRecognition text rescue on `onend` sends captured speech before mic-off.
- **Future:** Newer hardware with independent media pipelines eliminates this. Native app (Play Store) planned.
