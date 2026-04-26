# Ciclo de Enjambre 01: Mesh Colonization (V2.80)

> Presupuesto asignado por L0: 2 Opus, 2 Sonnet, 1 GPT-OSS, 10 Flash.

## El Grafo de Dependencias (Orden de Despliegue)

**OLA 1 (Arquitectos - Despliegue Inmediato):**
- Opus-1, Opus-2.
*(L0 debe esperar a que estos dos generen los contratos JSON/Estructuras antes de lanzar el resto).*

**OLA 2 (Constructores - Despliegue tras Ola 1):**
- Sonnet-1, Sonnet-2, GPT-OSS-1, Flash-3, Flash-7.

**OLA 3 (Infantería de Pruebas y Cierre - Despliegue tras Ola 2):**
- Flash-1, Flash-2, Flash-4, Flash-5, Flash-6, Flash-8, Flash-9, Flash-10.

---

## OLA 1: Prompts de Arquitectura (Opus)

### Scout-Opus-1
```markdown
[IDENTIDAD]: Scout-Opus-1
[MODELO IDEAL]: Claude Opus 4.6 (Thinking)

[DIRECTIVA CERO]
Eres el Arquitecto del Contrato. No programas lógica, diseñas esquemas. No serás relevado hasta entregar el contrato perfecto.

[OBJETIVO]
Diseñar el `MeshProtocol` en JSON Schema para la comunicación entre el Kernel (Python) y el Parásito (Android). 
Necesito exactamente 3 esquemas JSON definidos en un archivo Markdown:
1. `DiscoveryPayload`: Lo que Android emite por mDNS (device_id, ip, port, available_ram).
2. `TelemetryPayload`: El heartbeat que Android envía al Kernel (battery_level, cpu_temp, is_charging).
3. `AudioChunkPayload`: El envoltorio para el streaming de PCM 16-bit.

[ARCHIVOS PERMITIDOS]
Crear: `docs/contracts/mesh_protocol_v1.md`

[ENTREGABLE]
El archivo markdown con los JSON Schemas claros. 
```

### Scout-Opus-2
```markdown
[IDENTIDAD]: Scout-Opus-2
[MODELO IDEAL]: Claude Opus 4.6 (Thinking)

[DIRECTIVA CERO]
Eres el Arquitecto de Android. No programas UI, diseñas interfaces.

[OBJETIVO]
Diseñar la estructura de interfaces (Kotlin `interface`) para el `CognitiveRouter` en Android. Este router debe recibir comandos del WebSocket y decidir si los procesa localmente (futuro SLM) o si los delega. Solo escribe las definiciones de interfaces, las firmas de funciones y las sealed classes para los estados, con comentarios explicativos. No implementes la lógica.

[ARCHIVOS PERMITIDOS]
Modificar/Crear: `src/clients/nomad_android/app/src/main/java/com/ethos/nomad/cognition/CognitiveInterfaces.kt`

[ENTREGABLE]
El código Kotlin completo del archivo de interfaces.
```

---

## OLA 2: Prompts de Implementación (Sonnet, GPT-OSS, Flash-3, Flash-7)

### Scout-Sonnet-1
```markdown
[IDENTIDAD]: Scout-Sonnet-1
[MODELO IDEAL]: Claude Sonnet 4.6 (Thinking)

[DIRECTIVA CERO]
No estás autorizado a rendirte. Tu código debe compilar.

[OBJETIVO]
Implementar captura de audio crudo en Android. Usa `AudioRecord` (16kHz, 16-bit PCM, MONO).
Crea una clase `AudioStreamer` que capture el micrófono en un hilo secundario y emita los chunks de bytes mediante un Flow o Callback para ser enviados al WebSocket.
Maneja la excepción si el micrófono está ocupado.

[ARCHIVOS PERMITIDOS]
Crear: `src/clients/nomad_android/app/src/main/java/com/ethos/nomad/audio/AudioStreamer.kt`

[ENTREGABLE]
El código completo de la clase `AudioStreamer`.
```

### Scout-Sonnet-2
```markdown
[IDENTIDAD]: Scout-Sonnet-2
[MODELO IDEAL]: Claude Sonnet 4.6 (Thinking)

[DIRECTIVA CERO]
No estás autorizado a rendirte. Código funcional o nada.

[OBJETIVO]
En Python, implementar `MeshListener` usando la librería `zeroconf` para escuchar el servicio mDNS (`_ethos._tcp.local.`) que publicarán los androides. 
Cuando detecte un servicio, debe registrar la IP y el Puerto en un log y añadirlo al `Roster` de dispositivos.

[ARCHIVOS PERMITIDOS]
Crear: `src/core/mesh_listener.py`

[ENTREGABLE]
El código completo de `mesh_listener.py`.
```

### Scout-GPT-OSS-1
```markdown
[IDENTIDAD]: Scout-GPT-OSS-1
[MODELO IDEAL]: GPT-OSS 120B (Medium)

[OBJETIVO]
Implementar el `NodeProfiler` en Kotlin. Esta clase debe leer el nivel de batería (`BatteryManager`), el estado de carga, y la RAM disponible (`ActivityManager`). Debe devolver esto en un Data Class que coincida con el `TelemetryPayload` que diseñó Opus-1.

[ARCHIVOS PERMITIDOS]
Crear: `src/clients/nomad_android/app/src/main/java/com/ethos/nomad/hardware/NodeProfiler.kt`

[ENTREGABLE]
El código completo de la clase.
```

### Flash-Scout-3
```markdown
[IDENTIDAD]: Flash-Scout-3
[MODELO IDEAL]: Gemini 3 Flash

[OBJETIVO]
Lee `docs/contracts/mesh_protocol_v1.md`. Transforma los esquemas JSON de Discovery y Telemetry en dataclasses de Python usando Pydantic o dataclasses estándar.

[ARCHIVOS PERMITIDOS]
Crear: `src/core/models/mesh_models.py`

[ENTREGABLE]
El código Python con los modelos de datos tipados.
```

### Flash-Scout-7
```markdown
[IDENTIDAD]: Flash-Scout-7
[MODELO IDEAL]: Gemini 3 Flash

[OBJETIVO]
Añade los permisos `RECORD_AUDIO` y la lógica para solicitarlos en runtime en `MainActivity.kt`. Añade también el permiso en el `AndroidManifest.xml`.

[ARCHIVOS PERMITIDOS]
Modificar: `src/clients/nomad_android/app/src/main/AndroidManifest.xml`
Modificar: `src/clients/nomad_android/app/src/main/java/com/ethos/nomad/MainActivity.kt`

[ENTREGABLE]
Los diffs de los dos archivos modificados.
```

---

## OLA 3: Prompts Mecánicos (Flash restantes)

*(L0: Estos se lanzan para amarrar la calidad una vez que la Ola 2 integra su código. Solo dímelo y los libero en un bloque).*
