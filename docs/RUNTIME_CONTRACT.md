# Contrato del runtime (Fase 1)

El **runtime** es el proceso que mantiene vivo el servicio (p. ej. FastAPI + WebSocket). No redefine la ética.

## Fuente de verdad ética

- Solo `EthicalKernel.process`, `EthicalKernel.process_chat_turn`, `EthicalKernel.process_natural` (y rutas documentadas que delegan en ellos) determinan acciones y modos.
- El LLM **no** decide política.

## Qué puede hacer el runtime sin violar el contrato

| Permitido | Ejemplo |
|-----------|---------|
| Arrancar ASGI / uvicorn con el mismo `app` | `python -m src.runtime`, `python -m src.chat_server`, `uvicorn src.chat_server:app` |
| Tareas async de **solo lectura** sobre el kernel | `src.runtime.telemetry.advisory_loop` (solo `DriveArbiter.evaluate`); opcional por sesión WebSocket si `KERNEL_ADVISORY_INTERVAL_S` > 0 |
| Health checks, logs, métricas | `GET /health` |
| Timers que llamen **solo** a APIs documentadas como seguras | p. ej. invocar `execute_sleep` en un proceso que tenga un kernel explícito (diseño futuro; no inyecta acciones) |

## Prohibido en segundo plano

- Crear `CandidateAction` y aplicarlos sin pasar por `process` / `process_chat_turn`.
- Sustituir MalAbs, buffer o Bayes por salidas de LLM o de augenesis.
- Bucle que “hable” por el usuario o modifique DAO/narrativa sin pasar por el kernel en las rutas previstas.

## Augenesis

Sigue **opcional** y fuera del ciclo por defecto ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

## Entrada unificada

- **`python -m src.runtime`** — mismo servidor que `python -m src.chat_server` (`CHAT_HOST`, `CHAT_PORT`).

## Persistencia (confidencialidad, no ética)

Guardar o restaurar snapshots **no** altera las reglas de decisión del kernel. En el MVP los checkpoints van **sin cifrado**; para despliegues sensibles el cifrado en reposo está **previsto** (p. ej. `cryptography` en Python) y se describe en [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md), no en este contrato.

## Integridad del sistema (futuro; no ética normativa)

Capas de **metacontrol / robustez** (p. ej. vigilancia de deriva, manipulación, fugas) pueden ayudar a que el runtime **preserve su coherencia operativa** sin sustituir a MalAbs ni al buffer. Diseño discutido en [docs/discusion/PROPUESTA_ROBUSTEZ_V6_PLUS.md](discusion/PROPUESTA_ROBUSTEZ_V6_PLUS.md); no forma parte del contrato hasta implementación y tests.
