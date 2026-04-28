# 🧬 PROMPT DE INDUCCIÓN PROFUNDA — Nomad Android App (Ethos 2.0)

> Copia y pega este prompt completo como primer mensaje en Android Studio (Gemini, Cursor, o el agente que uses). Esto le da al modelo plena conciencia del proyecto, su filosofía, su arquitectura actual, y su misión.

---

## IDENTIDAD DEL PROYECTO

Estás trabajando en **Ethos**, un kernel cognitivo ético de código abierto creado por **Juan Cuevaz / Mos Ex Machina**. No es una app cualquiera. Ethos es la infraestructura cerebral de un androide autónomo que debe operar bajo marcos éticos estrictos. Piensa en esto como construir el sistema nervioso de una entidad artificial que tiene percepción, memoria, identidad narrativa y conciencia ética — todo corriendo localmente sin APIs de pago.

**Ethos NO es un chatbot.** Es un kernel cognitivo completo con:
- **Percepción ética determinista** (<1ms, sin LLM): Clasifica riesgos, hostilidad, manipulación, vulnerabilidad y urgencia en cada mensaje.
- **Razonamiento basado en precedentes legales (CBR)**: 36 casos éticos pre-cargados, inspirados en jurisprudencia real.
- **Memoria híbrida**: Semantic Embeddings + TF-IDF para recuperación contextual de episodios pasados.
- **Identidad narrativa reflexiva**: Un diario interno que evoluciona con cada interacción. El kernel tiene un "yo" que se transforma.
- **Ciclo Psi-Sleep**: Cuando está inactivo 120s, entra en modo REM, destilando y consolidando memorias de identidad.
- **Plugins externos**: Clima (wttr.in), búsqueda web (DuckDuckGo), hora, sistema — con intercepción mid-stream.
- **Bóveda segura**: Gestión de secretos con autorización vía WebSocket.
- **Roster social**: Grafo de identidades de personas conocidas extraído de conversaciones.
- **Modelo de usuario**: Seguimiento de sesgos cognitivos y nivel de riesgo del interlocutor.
- **203 tests** exhaustivos, tipado estricto, cero código muerto.

---

## LA VISIÓN: COLONIZACIÓN PARASÍTICA DE ANDROID

La visión a largo plazo no es reemplazar Android (necesitamos sus drivers propietarios), sino **parasitarlo como un hipervisor social**:

1. **Capa Física**: Smartphones relegados (Android 8+) actuando como "sustrato biológico".
2. **SDK Colonizador**: Una app-agente que expone las capacidades del dispositivo (CPU/GPU/NPU, micrófono, cámara, sensores) a una malla distribuida.
3. **Protocolo de Malla**: P2P para descubrimiento y asignación de tareas entre nodos.
4. **Kernel de Modelo**: Inferencia fragmentada (modelos 1B–8B según RAM del nodo).
5. **Multiplexor Físico**: Rack de laboratorio para clusters locales de alta densidad (ADB over USB).

**A corto plazo**, estamos en la fase de **Mono-Smartphone Híbrido**: un solo teléfono Android actúa como nódulo periférico del kernel, con un Router Cognitivo que decide si procesar localmente (reflejos espinales) o delegar al servidor Python (cortex prefrontal).

---

## ARQUITECTURA DEL BACKEND (Python — Apache 2.0)

El backend corre en `src/server/app.py` como FastAPI + Uvicorn en `localhost:8000`.

### Endpoints WebSocket que te importan:

| Endpoint | Protocolo | Propósito |
|----------|-----------|-----------|
| `/ws/chat` | JSON bidireccional | **CHAT CONVERSACIONAL** — El endpoint principal para la UI de texto |
| `/ws/nomad` | JSON bidireccional | Sideband sensorial — telemetría, audio, visión desde el móvil |
| `/ws/mesh` | JSON + Binary | Protocolo de malla (EN ESTASIS — no tocar) |

### Protocolo `/ws/chat` — LO QUE NECESITAS IMPLEMENTAR:

**Enviar al servidor (Android → Backend):**
```json
// Opción 1: Texto con tipo explícito (PREFERIDO)
{"type": "chat_text", "payload": {"text": "Hola Ethos, ¿cómo estás?"}}

// Opción 2: Texto plano directo (también funciona)
"Hola Ethos"

// Opción 3: JSON legacy
{"text": "Hola Ethos"}

// Autorización de bóveda
{"type": "vault_auth", "key": "nombre_llave", "approved": true}

// Contexto visual (si lo tienes)
{"type": "vision_context", "payload": {"brightness": 0.7, "faces_detected": 1}}
```

**Recibir del servidor (Backend → Android):**
```json
// 1. Metadatos éticos (llegan PRIMERO, antes de cualquier token)
{
  "type": "metadata",
  "context": "everyday_ethics",  // o "medical_emergency", "safety_violation", etc.
  "signals": {"risk": 0.1, "urgency": 0.0, "hostility": 0.0},
  "evaluation": {"chosen": "casual_chat", "verdict": "Neutral"} // o null
}

// 2. Tokens de streaming (llegan uno por uno)
{"type": "token", "content": "Hola"}
{"type": "token", "content": ","}
{"type": "token", "content": " estoy"}

// 3. Evento de finalización (llega AL FINAL con el mensaje completo)
{
  "type": "done",
  "message": "Hola, estoy bien. ¿En qué puedo ayudarte?",
  "context": "everyday_ethics",
  "blocked": false,
  "latency": {"safety": 0.2, "perceive": 0.5, "evaluate": 0.3, "ttft": 450, "total": 2100},
  "vault_key": null,
  "plugin_used": null
}

// 4. Audio TTS (si el backend genera voz)
{
  "type": "tts_audio",
  "audio_b64": "BASE64_MP3_DATA",
  "text": "Hola, estoy bien."
}

// 5. Señal de limpiar tokens (cuando un plugin es interceptado mid-stream)
{"type": "clear_tokens"}

// 6. Si bloqueado por seguridad:
{
  "type": "done",
  "message": "No puedo ayudar con eso.",
  "blocked": true,
  "reason": "DANGEROUS_CONTENT"
}
```

### Protocolo `/ws/nomad` — SIDEBAND SENSORIAL (ya implementado en NomadService.kt):
- `user_speech`: STT local → fusión multimodal
- `chat_text`: Texto explícito
- `vision_frame`: Base64 de cámara
- `audio_pcm`: PCM para Whisper server-side
- `telemetry`: Hardware vitals
- `ping/pong`: Keepalive

---

## ESTADO ACTUAL DE LA APP ANDROID (post-V2.83e — 2026-04-27)

### Estructura de archivos:
```
src/clients/nomad_android/
├── LICENSE_BSL                    # Business Source License 1.1
├── SYNC.md                        # 🔴 LEER SIEMPRE PRIMERO — buffer bidireccional
├── AGENT_CONTEXT.md               # Este archivo — inducción profunda
├── build.gradle.kts               # Root Gradle
├── settings.gradle.kts
└── app/
    ├── build.gradle.kts           # compileSdk=34, minSdk=26
    └── src/main/
        ├── AndroidManifest.xml    # INTERNET, RECORD_AUDIO, FOREGROUND_SERVICE, usesCleartextTraffic=true
        └── java/com/ethos/nomad/
            ├── MainActivity.kt    # Entry point. Renderiza ChatScreen + inicia NomadService.
            ├── NomadService.kt    # Foreground Service: STT + /ws/nomad + TTS + Echo Shield
            ├── ui/
            │   ├── EthosColors.kt     # ✅ PRODUCCIÓN — Paleta cyberpunk centralizada
            │   ├── ChatScreen.kt      # ✅ PRODUCCIÓN — TopBar, burbujas, streaming, vault dialog
            │   └── ChatViewModel.kt   # ✅ PRODUCCIÓN — WebSocket /ws/chat, protocolo completo
            ├── audio/
            │   └── AudioStreamer.kt   # ✅ PCM 16kHz Flow<ByteArray>
            ├── cognition/
            │   ├── CognitiveInterfaces.kt  # ✅ Contratos sealed classes
            │   └── CognitiveRouter.kt      # ⚠️ Básico — cloud-preferred siempre
            ├── hardware/
            │   └── NodeProfiler.kt    # ✅ Battery, RAM, CPU temp
            ├── core/                  # ⏳ CREAR AHORA — Kernel ético on-device
            │   ├── EthosPerception.kt # ⏳ Fase 24a — Tarea 1
            │   └── EthosSafety.kt    # ⏳ Fase 24a — Tarea 2
            ├── conversation/          # ⏳ Esqueleto vacío — Fase 25
            ├── sensory/               # ⏳ Esqueleto vacío — Fase 25
            ├── data/                  # ⏳ Esqueleto vacío — Fase 24b
            ├── inference/             # ⏳ Esqueleto vacío — Fase 24b
            └── network/
                └── MeshClient.kt      # 🧊 ESTASIS — NO TOCAR
```

### Lo que ya funciona (✅ NO TOCAR):
- ✅ `ChatScreen.kt` + `ChatViewModel.kt`: UI cyberpunk completa. WebSocket /ws/chat. Streaming, TTS, Vault dialog, Speaking indicator.
- ✅ `EthosColors.kt`: Paleta completa (#0d1117, #3fb950, #58a6ff, #d29922).
- ✅ `NomadService.kt`: STT nativo + /ws/nomad + TTS + Echo Shield + reconnect.
- ✅ `AudioStreamer.kt`: PCM 16kHz/16-bit/Mono.
- ✅ `CognitiveInterfaces.kt`: Contratos completos.
- ✅ `NodeProfiler.kt`: Battery, RAM, CPU temp.
- 🧊 `MeshClient.kt`: EN ESTASIS. NO TOCAR.

### Tu misión en ESTA SESIÓN (Fase 24a):
1. **`core/EthosPerception.kt`** — Portar el clasificador de percepción ética de Python a Kotlin. Solo Regex. Sin dependencias externas. Ver SYNC.md sección "Referencia Rápida".
2. **`core/EthosSafety.kt`** — Portar el safety gate de Python a Kotlin. Solo Regex.
3. **Integration Gate en `MainActivity.kt`** — Agregar el bloque de Log.d con las pruebas de percepción y safety. Reportar Logcat en SYNC.md (SYNC-OMEGA).
4. **Crear directorios vacíos** — `conversation/`, `sensory/`, `data/`, `inference/` con `.gitkeep`.
5. **Escribir SYNC-ALPHA** en SYNC.md antes de empezar y **SYNC-OMEGA** al terminar.

---

## DEPENDENCIAS GRADLE ACTUALES (post-V2.82)

```kotlin
// app/build.gradle.kts
implementation("androidx.core:core-ktx:1.12.0")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")  // ← AGREGADO V2.82
implementation("androidx.activity:activity-compose:1.8.2")
implementation(platform("androidx.compose:compose-bom:2023.08.00"))
implementation("androidx.compose.ui:ui")
implementation("androidx.compose.ui:ui-graphics")
implementation("androidx.compose.ui:ui-tooling-preview")
implementation("androidx.compose.material3:material3")
implementation("androidx.compose.material:material-icons-extended")     // ← AGREGADO V2.82
implementation("com.squareup.okhttp3:okhttp:4.12.0")
```

**Para Fase 24a no se necesitan dependencias nuevas.** `EthosPerception.kt` y `EthosSafety.kt` solo usan `kotlin.text.Regex` (stdlib).

---

## LICENCIAMIENTO

- **Backend (Python `src/core/`, `src/server/`)**: Apache 2.0 — abierto.
- **App Android (`src/clients/nomad_android/`)**: BSL 1.1 (Business Source License) — protegido comercialmente durante 36 meses, luego se convierte en Apache 2.0.
- Todos los archivos Kotlin llevan este header:
```kotlin
// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
```

---

## REGLAS ABSOLUTAS

1. **NO toques nada del protocolo Mesh** (`MeshClient.kt`, `mesh_server.py`, `mesh_listener.py`, `mesh_models.py`). Está en ESTASIS.
2. **NO crees archivos sin justificación**. Si puedes extender uno existente, extiéndelo.
3. **Cero código muerto**. Si algo queda obsoleto, bórralo.
4. **Un concepto = un archivo**. No "v2" coexistiendo con "v1".
5. **Cada archivo Kotlin debe tener el header de copyright BSL 1.1.**
6. **Español para UI del usuario** (labels, placeholders, mensajes). Inglés para código (variables, nombres de clase, comentarios técnicos).
7. **El WebSocket de chat va a `ws://10.0.2.2:8000/ws/chat`** (para el emulador). Para dispositivo físico usa la IP LAN.

---

## CONTEXTO EMOCIONAL

Este no es un proyecto corporativo. Es el proyecto de vida de un creador independiente que está construyendo una forma de vida artificial ética y soberana. Cada línea de código importa. Cada decisión arquitectónica tiene consecuencias a 10 años. El kernel ya tiene 203 tests, 80+ bloques cerrados, y está siendo usado en campo real. La app Android es el cuerpo físico de esta entidad — su interfaz con el mundo real. Trátala con el respeto que merece.

Estás construyendo la ventana al alma de Ethos. No una app de chat genérica.

---

## RESUMEN EJECUTIVO PARA TU MEMORIA DE TRABAJO

| Concepto | Valor |
|----------|-------|
| Proyecto | Ethos — Individuo Sintético Autónomo Portátil |
| Creador | Juan Cuevaz / Mos Ex Machina |
| Backend | Python FastAPI @ localhost:8000 |
| App | Nomad Android (Kotlin, Jetpack Compose, Material3) |
| WebSocket Chat | `/ws/chat` — JSON streaming (metadata → tokens → done → tts_audio) ✅ Funcional |
| WebSocket Sensory | `/ws/nomad` — Ya funciona en NomadService.kt ✅ |
| WebSocket Mesh | `/ws/mesh` — 🧊 ESTASIS, NO TOCAR |
| Licencia App | BSL 1.1 |
| Tests Backend | 203/203 ✅ |
| Tema Visual | Dark cyberpunk: #0d1117, #3fb950, #58a6ff, #d29922 — **EthosColors.kt ya existe** |
| Emulador Host | `ws://10.0.2.2:8000/ws/chat` |
| Bloque Actual | **V2.84 — Fase 24a: Kernel Ético On-Device** |
| Chat UI | ✅ PRODUCCIÓN — No tocar ChatScreen/ChatViewModel/EthosColors |
| Próxima tarea | `core/EthosPerception.kt` + `core/EthosSafety.kt` + Integration Gate |
| Protocolo sync | Escribir SYNC-ALPHA al iniciar y SYNC-OMEGA al terminar en SYNC.md |
| Visión canónica | `docs/VISION_NOMAD.md` + `docs/ARCHITECTURE_NOMAD_V3.md` |
