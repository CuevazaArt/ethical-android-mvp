# Plan por fases: runtime → persistencia → LLM local

Objetivo: avanzar de investigación a **proceso vivo** sin que ninguna capa pueda **contradecir la ética del kernel**. El núcleo decisorio sigue siendo `EthicalKernel` (MalAbs, Bayes, polos, voluntad); todo lo demás es percepción, tono, estado y almacenamiento.

---

## Principios que no se negocian

1. **Ningún bucle en segundo plano** elige acciones ni inyecta `CandidateAction` que no hayan pasado por `process` / `process_chat_turn`. Los *drives* y el monólogo **no** sustituyen al kernel.
2. **El LLM** (local o API) **no decide** política; solo traduce señales ↔ texto y estilo (ya acordado en teoría).
3. Cualquier “interrupción” o alerta al usuario es **capa de UX** (notificación), no un segundo veto paralelo a MalAbs.
4. **Augenesis** sigue **opcional** y fuera del ciclo por defecto ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

---

## Fase 1 — Runtime de ejecución (prioridad)

**Meta:** un proceso que **sigue vivo**, atiende I/O (chat/WebSocket) y puede programar tareas auxiliares **sin bloquear** la conversación, sin cambiar la semántica ética.

| Subfase | Qué hacer | Límites éticos |
|--------|-----------|----------------|
| **1.1 Contrato** | Documentar en código (docstring o `docs/`) qué tareas async están permitidas: p. ej. timers para `execute_sleep`, health, métricas. | Prohibido: tareas que llamen a APIs de “decisión” fuera de `process` / `process_chat_turn`. |
| **1.2 Baseline actual** | `python -m src.runtime` y `python -m src.chat_server` levantan el mismo ASGI (`get_uvicorn_bind` / `run_chat_server`). Ver [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). | Sin duplicar lógica ética fuera del kernel. |
| **1.3 Orquestación async** | Introducir un módulo delgado (p. ej. `src/runtime/`) que: (a) arranque el servidor ASGI; (b) opcionalmente registre **una** tarea de fondo para “mantenimiento” (p. ej. recordatorio interno de ejecutar `execute_sleep` en horario simulado o por evento explícito). | El fondo **no** genera respuestas al usuario ni modifica pesos éticos; como mucho encola un evento que el **mismo** flujo de chat podría consumir (fase posterior). |
| **1.4 Monólogo / drives en fondo** | Solo **telemetría**: logs o cola interna de “impulsos” derivados de `DriveArbiter.evaluate(kernel)` ya existente, sin LLM obligatorio en el bucle. | Si más adelante hay LLM para monólogo privado, va en Fase 3 y sigue siendo solo texto, no acción. |

**Entregable Fase 1:** proceso documentado + entrypoint claro + tests de que el kernel no se llama desde sitios no listados (opcional: test estático o convención).

**Orden sugerido:** 1.2 → 1.1 → 1.3 → 1.4.

**Estado en el repo (Fase 1.3–1.4):** si `KERNEL_ADVISORY_INTERVAL_S` es un número positivo, cada conexión `/ws/chat` arranca `advisory_loop` en segundo plano y lo detiene al cerrar la sesión (`src/chat_server.py`, `src/runtime/telemetry.py`). Sin decisión ni LLM; solo `DriveArbiter.evaluate` periódico.

---

## Fase 2 — Persistencia y base de datos

**Meta:** que identidad y episodios **sobrevivan** al reinicio, con esquema versionado.

| Subfase | Qué hacer | Notas |
|--------|-----------|--------|
| **2.1 Puerto** | DTO `KernelSnapshotV1` + `extract_snapshot` / `apply_snapshot` en `src/persistence/kernel_io.py`. | Cubre episodios, identidad, perdón, debilidad, Bayes/locus/variabilidad, DAO audit, `pruned_actions`. |
| **2.2 Adaptador JSON** | `JsonFilePersistence` (`src/persistence/json_store.py`). | Tests: `tests/test_persistence.py` (roundtrip en memoria, archivo, doble serialización). |
| **2.2b SQLite (opcional)** | Mismo DTO, otra columna `blob` JSON. | `SqlitePersistence` en `src/persistence/sqlite_store.py` (tabla `kernel_snapshot`, fila `id=1`). |
| **2.3 Cifrado (previsto, no MVP)** | Para despliegues con datos sensibles en disco, será **necesaria** una capa de cifrado sobre el snapshot (JSON/SQLite) o columnas; el candidato habitual en Python es la biblioteca **`cryptography`**, con **clave fuera del repo** (gestor de secretos / variable de entorno). | **Aún no implementado** — el MVP guarda texto plano a propósito. No sustituye permisos del SO ni control de acceso; documentar modelo de amenazas al añadirlo. |
| **2.4 Integración runtime** | WebSocket (`src/chat_server.py`): `try_load_checkpoint` al abrir conexión; `on_websocket_session_end` al cerrar; `maybe_autosave_episodes` tras cada turno. Env: `KERNEL_CHECKPOINT_*` (ver `src/persistence/checkpoint.py`). | Concurrencia: un archivo compartido entre varias conexiones puede pisarse. |

**Dependencia:** Fase 1 estable (al menos entrypoint y ciclo de vida del proceso).

---

## Fase 3 — LLM local (p. ej. Ollama)

**Meta:** percepción y voz **locales** para privacidad, sin cambiar quién decide.

| Subfase | Qué hacer | Límites |
|--------|-----------|---------|
| **3.1 Contrato LLM** | Extraer interfaz clara frente a `LLMModule`: `complete(system, prompt, …)` async o sync según el sitio de llamada. | Misma frontera que hoy: kernel llama solo a perceive/communicate/narrate. |
| **3.2 Adaptador Ollama** | `LLMModule` con `LLM_MODE=ollama`: `POST /api/chat` vía `httpx` (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`). | Si el modelo no devuelve JSON válido, cae al comportamiento local solo donde ya existía fallback; perceive/communicate/narrate esperan JSON en el prompt. |
| **3.3 Configuración** | Variables de entorno: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, flag `USE_LOCAL_LLM=true`. | Documentar en README. |
| **3.4 Monólogo con LLM (opcional)** | Solo después de 3.2: generar texto de monólogo interno para logs/UI, **nunca** como entrada directa a MalAbs. | Revisión de prompts para que no “instruyan” al kernel. |

**Estado en el repo (Fase 3):** `src/modules/llm_backends.py` (`TextCompletionBackend`, `OllamaCompletion`, `AnthropicCompletion`); `LLMModule` usa el backend según `resolve_llm_mode` / `LLM_MODE` / `USE_LOCAL_LLM`; monólogo opcional vía `KERNEL_LLM_MONOLOGUE` en `optional_monologue_embellishment` (chat). README documenta `OLLAMA_*`, modelo por defecto `llama3.2:3b`, y tests en `tests/test_ollama_llm.py`, `tests/test_llm_phase3.py`.

**Dependencia:** Fase 1 útil para no bloquear el event loop; Fase 2 independiente (persistencia puede ir antes o después del LLM local según prioridad de privacidad vs datos).

---

## Orden global recomendado

1. **Fase 1** (runtime + contrato + entrypoint + tareas de fondo seguras).  
2. **Fase 2** (persistencia: puerto → SQLite/JSON → integración arranque/parada).  
3. **Fase 3** (Ollama u otro backend local detrás del puerto LLM).

Entre fases: actualizar [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md), [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) y README con “qué está implementado”.

---

## Qué no hacer hasta tener bases

- Sustituir `process` por un agente LLM “autónomo”.
- Mezclar augenesis en el camino por defecto sin opt-in.
- Background loops que invoquen LLM sin límites de frecuencia y sin tests.

---

## Referencias en el repo

- Runtime y estado: [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md)  
- Teoría y capas v6: [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)  
- Chat actual: `src/chat_server.py`, `src/kernel.py`
