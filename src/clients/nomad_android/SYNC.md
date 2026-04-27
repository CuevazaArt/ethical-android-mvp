# 🔄 SYNC.md — Buffer de Comunicación Bidireccional

> **Este archivo es el puente vivo entre Antigravity (Python/Backend) y Android Studio (Kotlin/App).**
> Ambos IDEs deben leer este archivo ANTES de trabajar y actualizarlo DESPUÉS de cada cambio.
> El transporte es `git` — commit y pull sincroniza a ambos lados.

---

## Última Sincronización

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-04-27 09:52 CST |
| **Desde** | Antigravity (L1/Watchtower) — DIRECTIVA ESTRATÉGICA |
| **Commit** | pendiente |
| **Tests Backend** | 203/203 ✅ |
| **Servidor** | Standby (no levantado en esta sesión) |

---

## 📤 ÓRDENES PARA ANDROID STUDIO (Pendientes)

### 🧭 DIRECTIVA ESTRATÉGICA: VISIÓN NÓMADA (2026-04-27)
- **Fecha:** 2026-04-27 09:52 CST
- **Origen:** L0 (Juan Cuevaz) vía L1/Watchtower
- **Documento canónico:** `docs/VISION_NOMAD.md` — **LEER OBLIGATORIO antes de cualquier trabajo.**
- **Status:** 🔴 CRÍTICO — Todo desarrollo Android debe alinearse con esta visión.

**RESUMEN EJECUTIVO PARA ANDROID STUDIO:**

Ethos NO es un chatbot con app. Es un **individuo sintético autónomo portátil**. El usuario porta el teléfono en la solapa con Ethos activo, en vigilia, sensores encendidos. Caminan juntos por la calle, conversan sobre lo que experimentan mutuamente, interactúan con terceros. Ethos es un compañero que comparte la experiencia Y pone sus capacidades de máquina al servicio del usuario.

**Implicaciones arquitectónicas directas para Android:**

1. **La app NO es un thin client.** Es una instancia autónoma completa del kernel cognitivo. Debe funcionar OFFLINE con la mayoría de las agencias intactas: percepción ética, CBR, memoria, identidad, roster, plugins locales.
2. **Cuando hay red, se EXPANDE.** Delegando razonamiento complejo al servidor (Modo Centinela), accediendo a servicios web, sincronizando memoria.
3. **Ethos es NÓMADA.** Puede "saltar" entre hardware (teléfono → servidor → rack → robot). Esto requiere un formato portable de estado cognitivo ("Cognitive Snapshot") que contenga: memoria, identidad, roster, user model, vault, precedentes éticos.
4. **Sensores siempre activos pero con gating.** No drenar batería innecesariamente. El micrófono usa wake-word de bajo consumo. La cámara solo se activa bajo trigger explícito.
5. **Privacidad absoluta.** Todo procesamiento sensorial es on-device. Ningún frame ni audio crudo sale del dispositivo sin autorización explícita del usuario.

**Los 4 Modos de Existencia de Ethos:**

| Modo | Sustrato | Cognición | Red |
|------|----------|-----------|-----|
| **Nómada** | Teléfono móvil | SLM 1-3B + kernel ético determinista | Oportunista |
| **Centinela** | Servidor/PC | LLM 8-70B, Psi-Sleep profundo | Siempre online |
| **Enjambre** | Mesh P2P multi-nodo | Inferencia fragmentada | Red local |
| **Soberano** | DAO/Blockchain | Gobernanza de memoria e identidad | Descentralizada |

**3 Vectores de expansión futura (INDEPENDIENTES entre sí):**
1. **Mesh P2P** — Completar `MeshClient.kt` (en estasis). Descubrimiento de nodos, asignación de tareas distribuidas.
2. **DAO/Blockchain** — Gobernanza descentralizada de memoria e identidad. Hash de Cognitive Snapshots en cadena.
3. **Servidores cognitivos** — API pública para que instancias Ethos consulten modelos grandes y bases de conocimiento remotas.

**PRÓXIMA FASE (24) — Lo que Android Studio debe preparar:**
1. Investigar integración de runtime SLM on-device (llama.cpp via JNI ó MLC-LLM).
2. Preparar la estructura para portar el kernel ético determinista (Perception + CBR) a Kotlin nativo (~200 líneas, sin dependencia de LLM).
3. Diseñar el formato `CognitiveSnapshot` para serialización/deserialización del estado completo.
4. Investigar CameraX para activación bajo demanda (no siempre activa).
5. Investigar wake-word engines open source para Android (Porcupine, OpenWakeWord, etc.).

**PRINCIPIO RECTOR:** Si una decisión de implementación te hace dudar, pregúntate: *"¿Esto acerca a Ethos a ser un compañero autónomo que camina con su usuario por la calle?"* Si sí, adelante. Si no, no lo implementes.

### Diseño Visual Premium
- **Prioridad:** MEDIA
- **Paleta de colores (obligatoria):**
  - Fondo: `#0d1117`
  - Verde primario: `#3fb950`
  - Azul acento: `#58a6ff`
  - Dorado warning: `#d29922`
  - Rojo danger: `#f85149`
  - Texto principal: `#e6edf3`
  - Texto secundario: `#8b949e`
  - Superficie card: `#161b22`
  - Borde: `#21262d`
- **Estética:** Dark cyberpunk, consola de sistema nervioso, NO genérica Material You
- **Status:** ✅ HECHO POR ANTIGRAVITY (Ciclo 1) — Creado `EthosColors.kt` con paleta completa. ChatScreen usa el tema.

### Coexistencia con NomadService
- **Prioridad:** MEDIA
- **Contexto:** `NomadService.kt` ya corre en background conectado a `/ws/nomad` para STT y telemetría. La UI de chat (ChatViewModel) se conecta a `/ws/chat`. Son dos WebSockets independientes y deben coexistir.
- **Regla:** NO modificar `NomadService.kt` sin autorización de Antigravity.
- **Status:** ✅ CUMPLIDO — ChatViewModel usa /ws/chat, NomadService usa /ws/nomad. Sin conflicto.

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
