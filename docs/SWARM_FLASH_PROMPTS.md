# Enjambre Flash — 5 Prompts Listos para Ejecutar

> Generado por L1 (2026-04-26). Cada prompt es auto-contenido.
> Orden de ejecución: Flash-Scout-1 PRIMERO, luego 2-5 en paralelo.

---

## Flash-Scout-1: PODA DE RAMAS MUERTAS

```
[IDENTIDAD]: Flash-Scout-1
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias. Ejecuta cada comando hasta completar la lista.

[OBJETIVO]
Eliminar todas las ramas remotas obsoletas del repositorio `CuevazaArt/ethical-android-mvp`. La única rama que debe sobrevivir es `origin/main`.

Ejecuta estos comandos en orden. Son 50 ramas. Hazlo en lotes de 10 para evitar errores de red:

LOTE 1:
git push origin --delete antigravity-team
git push origin --delete antigravity/hemisphere-refactor-proposal
git push origin --delete arch/tri-lobe-kernel-p0
git push origin --delete chore/prebuild-dashboard-ci-mock-llm
git push origin --delete claude/friendly-wing
git push origin --delete claude/upbeat-jepsen
git push origin --delete claude/wizardly-bhabha
git push origin --delete claude/youthful-kirch-cab768
git push origin --delete claude/agitated-moser-9ad65f
git push origin --delete claude/friendly-pike-3cf891

LOTE 2:
git push origin --delete claude/modest-lamport-5deadf
git push origin --delete claude/naughty-goldwasser-03086d
git push origin --delete copilot/explain-repository-structure
git push origin --delete copilot/review-project-and-model
git push origin --delete copilot/review-project-status
git push origin --delete copilot/revise-deprecated-branches
git push origin --delete copilot/actualiza-repo-revisa-documentacion
git push origin --delete copilot/actualiza-tu-rama-del-repo
git push origin --delete copilot/check-merged-changes
git push origin --delete copilot/check-pending-tasks

LOTE 3:
git push origin --delete copilot/desarrollo-ciclo-asignado
git push origin --delete copilot/elaborate-field-test-plan
git push origin --delete copilot/fix-chat-llm-local-conflicts
git push origin --delete copilot/master-copilot-incrementar-verticalmente
git push origin --delete copilot/review-documentation-pending-tasks
git push origin --delete copilot/review-main-branch
git push origin --delete copilot/revisar-novedades-proyecto
git push origin --delete copilot/revise-project-and-assume-work
git push origin --delete copilot/update-antigravity-directivas
git push origin --delete copilot/update-visitor-facing-docs

LOTE 4:
git push origin --delete copilot/vscode-mnzeup2f-ddi5
git push origin --delete cursor-dellware/offline-mode-knowledge-proposal
git push origin --delete cursor-team
git push origin --delete cursor/claude-bi-p0-01-bayesian-mode-contract
git push origin --delete cursor/g-04-llm-touchpoint-surface
git push origin --delete doc/collaborative-branches-convention
git push origin --delete feature/antigravity-dellware/harden-primitive-modules
git push origin --delete feature/bloque-36-4-harden
git push origin --delete feature/copilot-bloque-12
git push origin --delete kernel-for-Vusual-Std

LOTE 5:
git push origin --delete main-pre-commune
git push origin --delete main-whit-landing
git push origin --delete master-Cursor
git push origin --delete master-antigravity
git push origin --delete master-claude
git push origin --delete master-copilot
git push origin --delete master-cursorultra
git push origin --delete master-visualStudio
git push origin --delete master-visualstudio
git push origin --delete merge/master-all-20260415-210826
git push origin --delete refactor/pipeline-trace-core

Después limpia las ramas locales obsoletas:
git branch -D antigravity-team
git branch -D backup-v13.1-distributed-brain
git branch -D master-Cursor
git branch -D master-antigravity
git branch -D master-claude
git branch -D master-cursorultra
git branch -D master-visualStudio
git branch -D temp-antigravity-backup

Finalmente confirma con:
git branch -a

[ARCHIVOS PERMITIDOS]
Ninguno. Solo comandos git.

[ENTREGABLE]
Muestra el output de `git branch -a` final. Solo debe quedar `main` local y `remotes/origin/main`.
Sin saludos, sin despedidas.
```

---

## Flash-Scout-2: HEADERS APACHE 2.0 EN KERNEL PYTHON

```
[IDENTIDAD]: Flash-Scout-2
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias.

[OBJETIVO]
Agregar el siguiente header de licencia al inicio de CADA archivo `.py` en `src/core/` y `src/server/` que NO lo tenga ya. NO modificar ninguna otra línea del archivo.

Header a agregar (exactamente estas 3 líneas, antes de cualquier import):
# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

Archivos objetivo en src/core/:
- chat.py, ethics.py, identity.py, llm.py, memory.py, perception.py
- plugins.py, precedents.py, roster.py, safety.py, sleep.py
- stt.py, status.py, tts.py, user_model.py, vault.py, vision.py
- __init__.py (si existe)

Archivos objetivo en src/server/:
- app.py
- __init__.py (si existe)

Otros archivos .py en src/:
- chat_server.py, ethos_cli.py, main.py, __init__.py

[ARCHIVOS PROHIBIDOS]
- Todo dentro de src/clients/ (esos tienen licencia BSL, no Apache).
- Todo dentro de tests/.
- Todo fuera de src/.

[ENTREGABLE]
Lista de archivos modificados. Un commit con mensaje:
"Flash-Scout-2: Apache 2.0 headers on all kernel Python files"
Sin saludos, sin despedidas.
```

---

## Flash-Scout-3: HEADERS BSL EN SDK ANDROID

```
[IDENTIDAD]: Flash-Scout-3
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias.

[OBJETIVO]
Agregar el siguiente header de licencia al inicio de CADA archivo `.kt` en `src/clients/nomad_android/` que NO lo tenga ya. NO modificar ninguna otra línea.

Header a agregar (exactamente estas 3 líneas, antes del `package` declaration):
// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.

Archivos conocidos:
- src/clients/nomad_android/app/src/main/java/com/ethos/nomad/MainActivity.kt
- src/clients/nomad_android/app/src/main/java/com/ethos/nomad/NomadService.kt
- Cualquier otro .kt que exista en subdirectorios (ej. cognition/).

[ARCHIVOS PROHIBIDOS]
- Todo fuera de src/clients/nomad_android/.
- Archivos .py, .xml, .gradle, .md.

[ENTREGABLE]
Lista de archivos modificados. Un commit con mensaje:
"Flash-Scout-3: BSL 1.1 headers on all Android Kotlin files"
Sin saludos, sin despedidas.
```

---

## Flash-Scout-4: LIMPIEZA DE DOCUMENTACIÓN OBSOLETA

```
[IDENTIDAD]: Flash-Scout-4
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias.

[OBJETIVO]
Eliminar los siguientes archivos de la raíz del repositorio. Son documentos V1/legacy que han sido superados por AGENTS.md, CONTEXT.md y LICENSING_STRATEGY.md:

git rm CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md
git rm COPILOT_REQUEST_HEMISPHERE_REFACTOR.md
git rm CURSOR_REQUEST_HEMISPHERE_REFACTOR.md
git rm PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md
git rm PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md
git rm INTEGRATION_PULSE_ANALYSIS_2026_04_16.md
git rm COLLABORATIVE_BRANCHES.md
git rm ONBOARDING.md

Después verifica que ningún otro archivo .md en la raíz haga referencia a estos documentos eliminados. Si alguno los menciona (ej. README.md, CONTRIBUTING.md), elimina solo la línea o link que apunte al archivo borrado.

[ARCHIVOS PERMITIDOS]
- Los 8 archivos listados arriba (para eliminar).
- README.md, CONTRIBUTING.md (solo para limpiar referencias rotas).

[ARCHIVOS PROHIBIDOS]
- AGENTS.md, CONTEXT.md, LICENSING_STRATEGY.md, TRADEMARK.md, CHANGELOG.md, HISTORY.md, BIBLIOGRAPHY.md, SECURITY.md.
- Todo dentro de src/, tests/, docs/, scripts/.

[ENTREGABLE]
Output de `git status` mostrando los archivos eliminados. Un commit con mensaje:
"Flash-Scout-4: Prune 8 obsolete V1 docs from root"
Sin saludos, sin despedidas.
```

---

## Flash-Scout-5: ACTUALIZACIÓN DE README.md

```
[IDENTIDAD]: Flash-Scout-5
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias.

[OBJETIVO]
Reescribir `README.md` para reflejar el estado actual del proyecto Ethos V2. El README debe ser profesional, atractivo y orientado a atraer contribuidores y sponsors.

Estructura EXACTA del README:

1. **Título y tagline:**
   # Ethos — Ethical Android Kernel
   > An open-source cognitive kernel for building ethical, autonomous android systems.

2. **Badges (en una línea):**
   - Tests: 203 passing
   - License: Apache 2.0
   - GitHub Sponsors link

3. **¿Qué es Ethos?** (3-4 líneas máximo)
   Un kernel Python que implementa percepción ética, memoria narrativa, identidad reflexiva y razonamiento basado en precedentes legales. Diseñado para correr localmente con Ollama (sin APIs de pago).

4. **Características principales** (lista con emojis):
   - 🧠 Percepción ética determinista (<1ms, sin LLM)
   - ⚖️ Razonamiento basado en precedentes (CBR, 36 casos)
   - 💾 Memoria híbrida (Semantic Embeddings + TF-IDF)
   - 🪞 Identidad narrativa reflexiva (Journal + Neuroplasticity)
   - 🔌 Sistema de plugins extensible (Weather, Web, Time, System)
   - 🔐 Bóveda segura con autorización por WebSocket
   - 📱 Cliente Android nativo (Nomad SDK)
   - 🧪 203 tests, zero legacy imports

5. **Quick Start** (comandos mínimos para correr):
   ```bash
   pip install -r requirements.txt
   python -m src.chat_server
   # Open http://localhost:8000
   ```

6. **Architecture** (1 párrafo + link a CONTEXT.md)

7. **Licensing** (breve, con links a LICENSING_STRATEGY.md y LICENSE_BSL):
   - Kernel: Apache 2.0
   - Android SDK: BSL 1.1 (converts to Apache after 36 months)
   - Models: Proprietary

8. **Contributing** (2 líneas + link a CONTRIBUTING.md y AGENTS.md)

9. **Support the Project** (link a GitHub Sponsors)

NO incluir: historia del proyecto, diagramas complejos, listas de bloques cerrados, ni menciones a V1.

[ARCHIVOS PERMITIDOS]
- README.md (reescritura completa)

[ARCHIVOS PROHIBIDOS]
- Todo lo demás.

[ENTREGABLE]
El README.md completo y listo. Un commit con mensaje:
"Flash-Scout-5: Professional README for open-source launch"
Sin saludos, sin despedidas.
```

---

## Instrucciones para L0

1. **Ejecuta Flash-Scout-1 primero** (poda de ramas). Espera a que termine.
2. **Luego lanza 2, 3, 4 y 5 en paralelo** (cada uno en una ventana/tab distinta).
3. Cuando todos terminen, regresa a L1 y di `review` para validar la integración.
4. Si algún Scout falla, di `el agente falló en Flash-Scout-N` y L1 generará un prompt de corrección.
