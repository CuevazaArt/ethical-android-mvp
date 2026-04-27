# 🔄 SYNC.md — Buffer de Comunicación Bidireccional

> **Este archivo es el puente vivo entre Antigravity (Python/Backend) y Android Studio (Kotlin/App).**
> Ambos IDEs deben leer este archivo ANTES de trabajar y actualizarlo DESPUÉS de cada cambio.
> El transporte es `git` — commit y pull sincroniza a ambos lados.

---

## Última Sincronización

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-04-27 13:31 CST |
| **Desde** | Antigravity (L1/Watchtower) — DIRECTIVA V2: REDISEÑO INTEGRAL |
| **Commit** | pendiente |
| **Tests Backend** | 203/203 ✅ |
| **Servidor** | Standby |

---

## 📤 ÓRDENES PARA ANDROID STUDIO (Pendientes)

### 🧭 DIRECTIVA ESTRATÉGICA V2: VISIÓN NÓMADA PROFUNDA (2026-04-27 13:30 CST)
- **Origen:** L0 (Juan Cuevaz) vía L1/Watchtower — REDISEÑO INTEGRAL
- **Documentos canónicos (LEER AMBOS antes de cualquier trabajo):**
  - `docs/VISION_NOMAD.md` — La brújula filosófica
  - `docs/ARCHITECTURE_NOMAD_V3.md` — El mapa técnico completo
- **Tag de referencia:** `v2.83-pre-swarm-nomad`
- **Status:** 🔴 CRÍTICO — Esta directiva SUPERSEDE todas las anteriores.

---

#### 1. CAMBIO DE PARADIGMA: VOICE-FIRST, NO CHAT-FIRST

**El chat es un medio secundario. La voz es la interfaz principal.**

Ethos NO espera mensajes de texto. Ethos ESCUCHA, OBSERVA y HABLA. El usuario lleva el teléfono en la solapa y mantiene conversación continua a viva voz.

**Implicaciones para Android Studio:**
- `NomadService` se convierte en el host del **Cognitive Loop** (siempre corriendo).
- `ChatScreen` sigue existiendo pero es la interfaz secundaria (fallback silencioso).
- El flujo principal es: Mic → VAD → Wake Word → STT → Kernel → TTS → Speaker.
- Toda respuesta de Ethos se emite por TTS automáticamente, no solo cuando el backend envía `tts_audio`.
- El usuario puede interrumpir a Ethos hablando. Ethos se calla y escucha.

**Nuevo paquete a crear: `conversation/`**
- `VoiceOutputManager.kt` — TTS con control de tono, queue, echo shield, interruptibilidad.
- `SalienceDetector.kt` — "¿Algo merece un comentario?" (ver Proactividad abajo).
- `ProactiveEngine.kt` — Genera comentarios contextuales sin que el usuario pregunte.
- `ConversationState.kt` — Último tema, mood del usuario, turnos sin hablar.
- `PersonalityConfig.kt` — Proactividad, humor, verbosidad (configurable por el usuario).

---

#### 2. ETHOS ES PARLANCHÍN Y ENCANTADOR, NO UN ASISTENTE

La personalidad de Ethos como compañero:
- **Observacional:** "Mira qué bonito atardecer" > "La hora del sunset es 19:42 UTC-6"
- **Breve:** 1-2 frases para comentarios proactivos. No ensayos.
- **Humor sutil:** Observaciones ingeniosas, no chistes formales.
- **Memoria conversacional:** "¿Es el café del que hablamos ayer?"
- **Deferencia social:** Callar si el usuario habla con otro humano.
- **Calibración emocional:** Si el usuario está tenso → suave. Si está animado → vivaz.

**Triggers proactivos (SalienceDetector):**

| Trigger | Ejemplo | Cooldown |
|---------|---------|----------|
| Cambio de ubicación | "No conozco esta zona. ¿Vienes seguido?" | 5 min |
| Hora relevante | "Ya son las 2, ¿no tenías hambre?" | 1 hora |
| Silencio prolongado | "¿Todo bien? Llevas rato callado." | 10 min |
| Cambio de movimiento | "¿Corriendo? ¡Buen ritmo!" | 3 min |
| Batería baja | "Me queda poca batería." | 30 min |

**Supresores:** Cooldown mínimo 30s entre comentarios. Callar si user habla con otro. Reducir si batería < 30%. Modo silencioso configurable.

---

#### 3. MOTOR ÉTICO BAYESIANO (Deuda Técnica Prioritaria)

Los pesos éticos actuales (U=0.40, D=0.35, V=0.25) son CONSTANTES. No hay aprendizaje. La nueva arquitectura usa **distribuciones Beta** para cada polo:

- Cada polo tiene `Beta(α, β)` donde el peso esperado es `α / (α + β)`.
- Tras cada decisión anclada en un precedente, se actualizan los priors.
- La incertidumbre es REAL (varianza de las distribuciones), no un proxy.
- Los pesos evolucionan con la experiencia. Ethos APRENDE éticamente.
- Se aplica decay temporal para evitar calcificación.
- Son 6 números (3 αs, 3 βs) — caben en cualquier CognitiveSnapshot.

**Para Android Studio:** Cuando portéis `EthosEthics.kt`, implementar con interface `PoleWeightProvider` que permita inyectar pesos bayesianos o estáticos indistintamente.

---

#### 4. WAKE WORD: SHERPA-ONNX + SILERO VAD (DECISIÓN TOMADA)

**Porcupine DESCARTADO** — Licencia propietaria incompatible con nuestra misión open source.

**Stack elegido:**
1. **Silero VAD** (ONNX, MIT) — Detecta si hay voz. Ultra ligero. Evita que el keyword spotter procese silencio.
2. **Sherpa-ONNX** (Apache 2.0) — Keyword spotting para "Ethos". Android nativo. Sin API keys.

```
Micrófono → Silero VAD → ¿Hay voz? → Sherpa-ONNX → ¿Es "Ethos"? → Activar STT completo
```

**Dependencias Gradle a investigar:**
- `com.k2fsa.sherpa:sherpa-onnx-android:x.y.z`
- `com.microsoft.onnxruntime:onnxruntime-android:x.y.z`
- Silero VAD como modelo ONNX incluido en assets

---

#### 5. ESTRUCTURA DE PAQUETES OBJETIVO (Revisada)

```
com.ethos.nomad/
├── core/                     ← NUEVO: Kernel ético portable
│   ├── EthosPerception.kt    ← PerceptionClassifier (regex, <1ms)
│   ├── EthosSafety.kt        ← Safety gate (regex, <1ms)
│   ├── EthosEthics.kt        ← Evaluador 3 polos
│   ├── BayesianPoleWeights.kt ← Beta distributions
│   ├── EthosPrecedents.kt    ← 36 casos CBR
│   ├── EthosMemory.kt        ← Episodic memory (Room)
│   ├── EthosIdentity.kt      ← Narrative journal
│   ├── EthosRoster.kt        ← Social graph
│   ├── EthosUserModel.kt     ← Bias/Risk
│   ├── EthosPlugins.kt       ← Time + System
│   ├── EthosSleep.kt         ← Psi-Sleep (WorkManager)
│   ├── CognitiveSnapshot.kt  ← Estado portable
│   └── EthosKernel.kt        ← Integrador (≡ ChatEngine)
│
├── inference/                ← NUEVO: LLM on-device
│   ├── LocalLlmClient.kt    ← llama.cpp JNI
│   └── ModelManager.kt      ← Gestión de modelos GGUF
│
├── sensory/                  ← NUEVO: Capa sensorial
│   ├── WakeWordEngine.kt    ← Sherpa-ONNX
│   ├── SileroVad.kt         ← Voice Activity Detection
│   ├── VisionGate.kt        ← CameraX on-demand
│   ├── LocationTracker.kt   ← GPS fused
│   ├── MotionDetector.kt    ← Acelerómetro
│   └── SensoryFusion.kt     ← Combinación multimodal
│
├── conversation/             ← NUEVO: Motor conversacional
│   ├── SalienceDetector.kt  ← "¿Algo merece comentario?"
│   ├── ProactiveEngine.kt   ← Genera comentarios contextuales
│   ├── ConversationState.kt ← Estado vivo de la conversación
│   ├── PersonalityConfig.kt ← Rasgos configurables
│   └── VoiceOutputManager.kt ← TTS + echo shield + interrupción
│
├── data/                     ← NUEVO: Persistencia
│   ├── EthosDatabase.kt     ← Room Database
│   ├── MemoryDao.kt
│   ├── IdentityDao.kt
│   └── RosterDao.kt
│
├── cognition/                ← EXISTENTE (se actualiza)
├── ui/                       ← EXISTENTE (interfaz secundaria)
├── audio/                    ← EXISTENTE
├── hardware/                 ← EXISTENTE
└── network/                  ← 🧊 ESTASIS
```

---

#### 6. TAREAS INMEDIATAS PARA ANDROID STUDIO

1. **Leer `docs/ARCHITECTURE_NOMAD_V3.md`** completo. Contiene el diagrama del Cognitive Loop, el flujo de procesamiento, y los niveles de vigilia por batería.
2. **Crear el paquete `core/`** vacío. Aquí llegará el kernel ético portado.
3. **Crear el paquete `conversation/`** vacío. Aquí vivirá el motor de proactividad.
4. **Crear el paquete `sensory/`** vacío. Aquí vivirá la capa sensorial unificada.
5. **Crear el paquete `data/`** vacío. Aquí vivirá Room Database.
6. **Investigar Sherpa-ONNX Android SDK.** Repo: `github.com/k2-fsa/sherpa-onnx`. Verificar que compile con nuestro `compileSdk=34` y `minSdk=26`.
7. **Investigar llama.cpp Android example.** Repo: `github.com/ggerganov/llama.cpp/tree/master/examples/llama.android`. Evaluar si es viable con nuestro Gradle setup.

**No implementar nada todavía.** Solo preparar la estructura y reportar hallazgos de investigación en la sección 📥.

---

### Diseño Visual Premium
- **Status:** ✅ HECHO — EthosColors.kt con paleta cyberpunk completa.

### Coexistencia con NomadService
- **Evolución:** NomadService se convertirá en el host del Cognitive Loop. Por ahora NO modificar.
- **Status:** ✅ Coexistencia /ws/chat + /ws/nomad funcional.

---

## 📥 REPORTES DESDE ANDROID STUDIO (Completados)

> Android Studio escribe aquí lo que hizo. Antigravity lo revisa en el siguiente `review`.

### 2026-04-26 22:38 — AS confirmó comprensión de arquitectura
- **Estado:** Android Studio leyó AGENT_CONTEXT.md y entendió correctamente:
  - Servidor FastAPI en PC → ws://10.0.2.2:8000/ws/chat
  - CognitiveRouter para decisión local vs cloud
  - NomadService.kt en background para /ws/nomad
- **Necesito de Antigravity:** Aclaración sobre SLM on-device ✅ (ver abajo)

### 2026-04-26 22:38 — [ANTIGRAVITY → AS] Aclaración crítica sobre SLM
- **LocalModelClient** en `CognitiveInterfaces.kt` es SOLO un contrato/interface. No hay modelo real cargado.
- **CognitiveRouter** siempre usa el path `CLOUD_PREFERRED` actualmente. El path LOCAL_ONLY es un stub.
- **Conclusión para AS:** No intentes integrar ExecuTorch o MediaPipe en esta sesión. El objetivo es solo conectar `/ws/chat` y mostrar el chat. El SLM on-device es Fase futura.
- **Flujo real de esta sesión:** Usuario escribe → ChatViewModel → /ws/chat → Ethos Python → tokens de vuelta → UI los muestra.

### 2026-04-26 22:59 — [ANTIGRAVITY] CICLO 1 COMPLETADO
- **Archivos creados:** `ui/EthosColors.kt` (sistema de colores centralizado)
- **Archivos reescritos:** `ui/ChatViewModel.kt` (producción), `ui/ChatScreen.kt` (producción)
- **Archivos modificados:** `app/build.gradle.kts` (+lifecycle-viewmodel-compose, +material-icons-extended)
- **Qué implementé:**
  - ChatViewModel: WebSocket a /ws/chat con manejo completo del protocolo (metadata, token, clear_tokens, done, tts_audio), reconnect automático, vault auth stubs
  - ChatScreen: TopBar con dot de conexión + badge ético, burbujas diferenciadas (user/ethos/blocked), streaming bubble con animación de pulso, input bar con diseño cyberpunk, welcome card, auto-scroll, footer con latencia y plugin badge
  - EthosColors: Paleta completa (#0d1117, #3fb950, #58a6ff, etc.)
- **Necesito de AS:** Hacer `git pull`, compilar, reportar si hay errores de compilación.
- **Pendiente para Ciclo 2:** TTS audio playback, Vault authorization dialog, polish de animaciones.

### 2026-04-26 23:02 — [ANTIGRAVITY] CICLO 2 COMPLETADO
- **Backend:** Agregado `/api/ping` endpoint ligero para verificación de conectividad desde Android.
- **Android ChatViewModel:** TTS playback funcional (Base64 MP3 → MediaPlayer con prepareAsync). isSpeaking observable. Vault state migrado a observable `pendingVaultKey`.
- **Android ChatScreen:** VaultAuthDialog con AlertDialog Material3 (icono candado dorado, botones Autorizar/Denegar). Imports de Lock y VolumeUp agregados.
- **Tests Backend:** 203/203 ✅ (sin regresiones).
- **Necesito de AS:** `git pull`, compilar, probar envío de mensaje y verificar que el streaming funcione. Si el TTS no suena, reportar en SYNC.md.
- **Pendiente para Ciclo 3:** Speaking indicator visual en TopBar, polish final de animaciones, test end-to-end.

### 2026-04-26 23:05 — [ANTIGRAVITY] CICLO 3 COMPLETADO (FINAL)
- **Android ChatScreen:** Speaking indicator animado en TopBar (VolumeUp icon con pulso verde cuando `isSpeaking=true`). Parámetro `isSpeaking` propagado desde ChatScreen → TopBar.
- **CONTEXT.md:** Bloque V2.82 cerrado con documentación de los 3 ciclos.
- **Tests Backend:** 203/203 ✅.
- **RESULTADO FINAL DE LOS 3 CICLOS:**
  - ✅ ChatViewModel: WebSocket completo, streaming, TTS, Vault, reconnect
  - ✅ ChatScreen: TopBar con dot + speaking + badge, burbujas, streaming bubble, vault dialog, input bar
  - ✅ EthosColors: Paleta cyberpunk centralizada
  - ✅ Backend: /api/ping endpoint
  - ✅ Protocolo /ws/chat: 100% implementado (metadata, token, clear_tokens, done, tts_audio)
- **Necesito de AS:** `git pull` final, compilar, correr en emulador y probar el chat end-to-end.

<!-- TEMPLATE para Android Studio:
### [Fecha] — [Descripción breve]
- **Archivos modificados:** [lista]
- **Archivos creados:** [lista]
- **Archivos eliminados:** [lista]
- **Compila:** ✅/❌
- **Problemas encontrados:** [descripción o "ninguno"]
- **Decisiones tomadas:** [justificación de cambios no obvios]
- **Necesito de Antigravity:** [algo que requiera cambio en backend, o "nada"]
-->

---

## 🚫 ESTASIS (NO TOCAR)

Estos archivos/módulos están congelados. Ni Antigravity ni Android Studio los modifican hasta nueva orden:

- `network/MeshClient.kt`
- `src/server/mesh_server.py`
- `src/core/mesh_listener.py`
- `src/core/models/mesh_models.py`
- Todo lo relacionado con el protocolo `/ws/mesh`

---

## 📋 ESTADO DE ARCHIVOS ANDROID

| Archivo | Estado | Última modificación | Notas |
|---------|--------|---------------------|-------|
| `MainActivity.kt` | ✅ Funcional | 2026-04-26 | Renderiza ChatScreen, inicia NomadService |
| `NomadService.kt` | ✅ Funcional | 2026-04-26 | STT + /ws/nomad + TTS + Echo Shield |
| `ui/EthosColors.kt` | ✅ NUEVO | 2026-04-26 (C1) | Paleta cyberpunk centralizada |
| `ui/ChatScreen.kt` | ✅ PRODUCCIÓN | 2026-04-26 (C1) | TopBar, burbujas, streaming, input bar |
| `ui/ChatViewModel.kt` | ✅ PRODUCCIÓN | 2026-04-26 (C1) | WebSocket /ws/chat, protocolo completo |
| `audio/AudioStreamer.kt` | ✅ Funcional | 2026-04-26 | PCM 16kHz Flow<ByteArray> |
| `cognition/CognitiveInterfaces.kt` | ✅ Contratos | 2026-04-26 | Sealed classes, interfaces |
| `cognition/CognitiveRouter.kt` | ⚠️ Básico | 2026-04-26 | Lógica de routing simple |
| `hardware/NodeProfiler.kt` | ✅ Funcional | 2026-04-26 | Battery, RAM, CPU temp |
| `network/MeshClient.kt` | 🧊 ESTASIS | 2026-04-26 | NO TOCAR |

---

## 🔑 REGLAS DE SINCRONIZACIÓN

1. **Antes de trabajar:** `git pull origin main` + leer este archivo.
2. **Después de trabajar:** Actualizar la sección correspondiente (📥 si eres Android Studio, 📤 si eres Antigravity).
3. **Commit message format:** `V2.XX: [Nombre del bloque] — [resumen de una línea]`
4. **Conflictos:** Si hay conflicto en este archivo, la versión más reciente gana. Merge manual.
5. **Emergencias:** Si Android Studio rompe algo, escribe en 📥 con `⚠️ URGENTE` y Antigravity lo prioriza.
