# Runtime persistente (diseño inicial)

Este documento **no** prescribe implementación inmediata; fija criterios para cuando el kernel deje de ser solo demos efímeras y pase a procesos de larga duración con estado recuperable.

## Objetivo

Un **runtime persistente** mantiene identidad narrativa, memoria episódica y gobernanza auditada entre reinicios, sin alterar el contrato ético del núcleo (MalAbs → Bayes → polos → voluntad; capas v6 solo lectura para tono).

## Estado que habría que externalizar

| Área | Contenido hoy (RAM) | Riesgo si solo vive en proceso |
|------|---------------------|--------------------------------|
| Episodios | `NarrativeMemory` | Pérdida total al reiniciar |
| Identidad | `NarrativeIdentityTracker` | Idem |
| Perdón / carga | `AlgorithmicForgiveness`, `WeaknessPole` | Drift no guardado |
| STM chat | `WorkingMemory` | Por diseño corto; puede quedar solo en sesión |
| Inmortalidad | `ImmortalityProtocol` | Snapshots ya conceptualmente “backup”; falta almacén real |
| Variabilidad | `VariabilityEngine` (semilla) | Reproducibilidad entre entornos |

## Línea base reproducible

- **`AugenesisEngine`** permanece **opcional** y fuera del ciclo `process` / `execute_sleep` por defecto (ver [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)). Los experimentos con perfiles sintéticos no deben mezclarse con la línea base de validación sin opt-in explícito.
- Un runtime persistente debería versionar **esquema de snapshot** (episodios + identidad + metadatos) y tests de migración incremental.

## Implementación actual (Fase 2 — MVP)

- **`src/persistence/`** — `KernelSnapshotV1` + `extract_snapshot` / `apply_snapshot` (estado mutable del kernel sin tocar algoritmos éticos).
- **`JsonFilePersistence`** — guarda/carga JSON UTF-8 en ruta configurable (`save` / `load` / `load_into_kernel`).
- **`checkpoint.py`** — integración WebSocket: carga al abrir sesión, guardado al cerrar y autosave cada N episodios (variables `KERNEL_CHECKPOINT_*`).
- **Cifrado** — aún no integrado; ver checklist de seguridad abajo.

## Fronteras recomendadas (hexagonal, incremental)

1. **Puerto de persistencia** — el DTO v1 actúa como snapshot completo; siguientes adaptadores (SQLite, cifrado) pueden mapear al mismo esquema o a una versión `schema_version++`.
2. **Puerto LLM** — ya implícito en `LLMModule`; un segundo proveedor fuerza límites claros.
3. **Proceso de servicio** — `chat_server` como frontal WebSocket; workers opcionales para `execute_sleep` programado sin bloquear chat.

## Operación y despliegue

- Health checks (`/health` ya en `chat_server`) y límites de conexión por instancia.
- Un kernel por conexión WebSocket es adecuado para aislamiento; un runtime “multi-tenant” exigiría separación fuerte de estado y cuotas.

## Plan por fases (detalle)

Implementación escalonada: **primero runtime**, luego **persistencia/DB**, luego **LLM local (Ollama)** — con límites éticos explícitos en cada fase. Ver [RUNTIME_FASES.md](RUNTIME_FASES.md).

**Contrato del runtime (Fase 1):** [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

## Próximos pasos sugeridos

1. Definir un **DTO de snapshot mínimo** (serializable JSON o msgpack) alineado con lo que ya expone `ImmortalityProtocol` / episodios.
2. Añadir un adaptador **filesystem** detrás del puerto, sin cambiar `EthicalKernel.process`.
3. Pruebas de idempotencia: restaurar → mismo comportamiento ético en escenarios fijos (misma semilla de variabilidad).

Cuando esto exista en código, actualizar [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) y el README con la ruta del adaptador por defecto.
