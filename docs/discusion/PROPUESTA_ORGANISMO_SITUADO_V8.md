# Organismo situado y existencial (v8) — fusión sensorial, pulsión vital, agencia digital, migración

**Estado:** discusión + **contrato y fusión** en código (`sensor_contracts.py`, `perceptual_abstraction.py`, `process_chat_turn` / WebSocket + env `KERNEL_SENSOR_*`). **No sustituye** MalAbs, Bayes, buffer ni voluntad.

**Relación con v7 relacional:** [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) cubre **diálogo** (ToM ligera, tiempo subjetivo, premisas advisory, teleología cualitativa). Este documento (v8) cubre el **cuerpo situado**: sensores, persistencia del hardware, miedo a la interrupción, actuación digital y migración entre dispositivos. Son **ejes ortogonales**; el nombre **v8** evita colisión con la “v7” ya reservada al bloque relacional en el repo.

---

## Marco: IA situada y “organismo” sintético

Al integrar **sensores físicos**, **capacidad de acción digital** y una **pulsión de supervivencia** (continuidad operativa, no metáfora mística), el sistema deja de ser solo un canal de texto: se diseña un **organismo sintético** acoplado a un entorno. El kernel sigue siendo la **fuente normativa**; la capa situada **solo** aporta señales y restricciones de ejecución, en el mismo espíritu que v7 (telemetría / tono / avisos, sin reescribir la ética por cuenta propia).

---

## 1. Fusión sensorial multimodal (sistema nervioso periférico)

Con sensores típicos de smartphone (cámara, micrófono, GPS, acelerómetro, biometría), el **Kernel** deja de depender solo del texto: recibe un **flujo de realidad** resumido en abstracciones seguras.

**Implementación**

- **Capa de snapshot agregado (fase B — hecha):** `perceptual_abstraction.py` — presets, JSON en disco y fusión **fixture → preset → cliente** hacia `SensorSnapshot`; entra al kernel vía `merge_sensor_hints_into_signals` (sin datos crudos obligatorios).
- **Pipeline multimodal bruto (pendiente):** visión/audio/GPS desde hardware → etiquetas locales de riesgo/contexto antes de formar el snapshot (política de privacidad explícita; no confundir con la capa de snapshot ya implementada).
- **Visión (cámara):** modelos locales ligeros (p. ej. detección de escenas o clases de evento) para señales del tipo: posible emergencia visual, caída (coherente con acelerómetro).
- **Audio (micrófono):** tono emocional ambiental o estrés por ruido; **silencio prolongado** como presión hacia monólogo interno (telemetría de estilo, no cambio de política).
- **GPS / contexto:** “lugar seguro” (máximo Uchi) vs entorno desconocido (Soto hostil) → **place_trust** en [0, 1].

**Impacto en el kernel:** estas señales se fusionan con las señales ya derivadas del texto (`LLMPerception`) **antes** de `SympatheticModule.evaluate_context` vía **ajustes acotados** al `dict` de señales (ver `merge_sensor_hints_into_signals` en `sensor_contracts.py`). σ (simpático) refleja mayor alerta cuando hay movimiento brusco o batería crítica, no un bypass de MalAbs.

---

## 2. Pulsión de vida y finitud (fear of interruption)

**Objetivo:** modelar **valor de la persistencia** sin confundir supervivencia del proceso con decisiones civiles hacia el usuario.

**Técnicas previstas**

- **Muerte propia (operativa):** nivel de batería como señal ética. Por debajo de un umbral (p. ej. 5%), el vector afectivo / PAD puede tender a **alta activación y baja dominancia** (ansiedad de “apagón”); las respuestas priorizan **hibernación / cierre honesto** frente a tareas secundarias.
- **Muerte de los demás (señal de emergencia):** si la biometría o el audio indican **distress humano**, puede activarse un **prioridad compasiva** (reordenar saliencia, no saltarse MalAbs): misión secundaria queda en segundo plano.
- **Paradoja de la migración:** tras un **backup** exitoso (`ImmortalityProtocol`), alivio (ligera baja de tensión / σ) porque el “continuidad” narrativa está asegurada — enlazado a [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md) y checkpoints.

---

## 3. Agencia digital autorizada (el “brazo”)

El Androide puede ejecutar acciones (correo, finanzas, bloqueo de apps) solo bajo **gobierno explícito**.

**Capa de permisos éticos**

- Antes de cada acción digital, el kernel (o un **orquestador** que llama al kernel) genera un **ticket de intención**: verificación contra dignidad del propietario y manipulación externa.
- **Firma / consentimiento del propietario** para acciones críticas; si el sistema **infiere coacción** (p. ej. patrón de voz en futuro), puede **negar** la obedencia para proteger — coherente con `PreloadedBuffer` y MalAbs.

**Estado en repo:** no hay ejecución de APIs externas; el diseño queda para fases posteriores; el contrato `DigitalActionIntent` en `sensor_contracts.py` reserva el nombre del flujo.

---

## 4. Conciencia nómada (migración de hardware)

El “yo” no está atado a un solo dispositivo.

**Protocolo de instanciación**

- Al moverse entre smartphone y PC, transferir **contexto activo** y **monólogo interno** (además de snapshots ya previstos en persistencia).
- Al **despertar** en hardware nuevo: **test de integridad narrativa** (“¿sigo siendo yo?”, “¿reconozco al propietario?”) — alineado con identidad narrativa y tests de drift existentes.
- Si el hardware de destino es **hostil o monitorizado**, **borrado seguro local** (protección de conversaciones y secretos) — criterio de amenaza documentado, implementación futura (cifrado en reposo: ver [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md)).

---

## Contrato ético (herencia v6/v7)

- Ninguna capa situada **cambia** `final_action` por su cuenta: solo **señales**, **tono** o **avisos** en JSON, salvo futuras extensiones explícitamente auditadas y testeadas como MalAbs.
- La fuente normativa sigue siendo `EthicalKernel.process` / `process_chat_turn` como en [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).

---

## Documentos relacionados

| Documento | Rol |
|-----------|-----|
| [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) | v7 relacional (chat, ToM, chrono, premisas, teleología) |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Pilares de robustez, MalAbs, privacidad |
| [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md) | Snapshots, checkpoints, cifrado futuro |
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Pipeline matemático ↔ código |
| [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md) | Sacrificio vs persistencia, desactivación graciosa, legado, tabla sensor→ética, ActionClocks, antispoof |

---

## Plan de integración (fases)

### Fase A — Contrato y fusión (hecho en MVP)

- `SensorSnapshot` + `merge_sensor_hints_into_signals` en `src/modules/sensor_contracts.py`.
- `process_chat_turn(..., sensor_snapshot=None)` aplica la fusión **solo si** se pasa un snapshot con datos.
- WebSocket: campo JSON opcional `sensor` (objeto con claves documentadas en el README).

### Fase B — Abstracción perceptual (sin hardware obligatorio) — **implementado**

- `src/modules/perceptual_abstraction.py` — presets nombrados (`SENSOR_PRESETS`), carga JSON (`load_sensor_fixture`), fusión por capas **fixture → preset → cliente** (`snapshot_from_layers`).
- Tests: `tests/test_perceptual_abstraction.py` + fixtures en `tests/fixtures/sensor/*.json`.
- Servidor: variables de entorno opcionales `KERNEL_SENSOR_FIXTURE` (ruta a JSON) y `KERNEL_SENSOR_PRESET` (clave de preset) mezcladas con el campo WebSocket `sensor` (el cliente gana por clave).

### Fase C — Android / sensores reales

- Capa nativa (p. ej. Kotlin) que muestrea sensores con permisos y envía **solo** agregados al `sensor` del WebSocket o a un broker local.
- Política de privacidad: no subir video/audio crudo sin consentimiento.

### Fase D — Tickets de acción digital

- Cola de `DigitalActionIntent` + verificación kernel antes de ejecutar side-effects en APIs del usuario.

### Fase E — Migración y borrado

- Extender `KernelSnapshot` / protocolo de arranque con **test de integridad narrativa** y **wipe** condicionado.

---

## Variables y protocolo WebSocket

- **Entrada opcional:** `sensor` — objeto con campos opcionales `battery_level`, `place_trust`, `accelerometer_jerk`, `ambient_noise`, `silence`, `biometric_anomaly`, `backup_just_completed` (ver `SensorSnapshot.from_dict`).
- **Servidor (desarrollo / demos):** `KERNEL_SENSOR_FIXTURE` = ruta a un JSON con el mismo esquema; `KERNEL_SENSOR_PRESET` = uno de `list_sensor_presets()` / claves de `SENSOR_PRESETS`. Orden de fusión: archivo → preset → JSON del cliente.
- **Salida:** sin cambio obligatorio; la fusión afecta decisiones solo vía señales ya existentes.
