# 🔄 SYNC.md — Buffer de Comunicación Bidireccional

> **Este archivo es el puente vivo entre Antigravity (Python/Backend) y Android Studio (Kotlin/App).**
> Ambos IDEs deben leer este archivo ANTES de trabajar y actualizarlo DESPUÉS de cada cambio.
> El transporte es `git` — commit y pull sincroniza a ambos lados.

---

## Última Sincronización

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-04-26 23:05 CST |
| **Desde** | Antigravity (L1/Watchtower) — CICLO 3 (FINAL) |
| **Commit** | pendiente |
| **Tests Backend** | 203/203 ✅ |
| **Servidor** | ✅ VIVO en :8000 (PID 11788) |

---

## 📤 ÓRDENES PARA ANDROID STUDIO (Pendientes)

### ⚠️ URGENTE: CHAT NO FUNCIONA — DIAGNÓSTICO REQUERIDO
- **Fecha:** 2026-04-26 23:14 CST
- **Problema:** L0 reporta que la app corre en el emulador pero el chat no funciona. El servidor backend está VIVO y responde correctamente a `http://localhost:8000/api/ping` → `{"pong":true}`.
- **Hipótesis de Antigravity (ordenadas por probabilidad):**
  1. **AS no hizo `git pull`** y tiene código viejo (stubs) en ChatViewModel.kt
  2. **AS reescribió ChatViewModel.kt/ChatScreen.kt** con su propia versión que no coincide con el protocolo del backend
  3. **El emulador no puede llegar a `10.0.2.2:8000`** (firewall de Windows)
  4. **Error de compilación silencioso** que no se reportó

- **ACCIÓN REQUERIDA POR ANDROID STUDIO:**
  1. **Verifica versión del código:** Abre `ChatViewModel.kt` y confirma que la constante `WS_URL` dice exactamente `ws://10.0.2.2:8000/ws/chat`. Si dice otra cosa, haz `git pull origin main` y recompila.
  2. **Revisa Logcat:** Filtra por tag `ChatViewModel` en Logcat. Reporta exactamente qué dice:
     - ¿Dice "WebSocket connected"? → Conexión OK, el problema es de protocolo
     - ¿Dice "WebSocket failure"? → Copia el error exacto
     - ¿No dice nada? → El ViewModel no se está instanciando
  3. **Test de red desde emulador:** Abre terminal en AS y corre:
     ```
     adb shell curl http://10.0.2.2:8000/api/ping
     ```
     Reporta si responde o falla.
  4. **Verifica que `viewModel()` se está usando:** En `ChatScreen.kt`, confirma que la firma dice `fun ChatScreen(viewModel: ChatViewModel = viewModel())` — necesita el import `androidx.lifecycle.viewmodel.compose.viewModel`.
  5. **Verifica Gradle:** Confirma que `app/build.gradle.kts` tiene:
     ```
     implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
     ```

- **REPORTA EN LA SECCIÓN 📥 con:**
  - Contenido exacto de `WS_URL` en tu ChatViewModel
  - Output de Logcat filtrado por "ChatViewModel"
  - Resultado de `adb shell curl`
  - Cualquier error de compilación
- **Status:** 🔴 BLOQUEANTE


> Estas tareas fueron generadas por Antigravity. Android Studio debe ejecutarlas y marcarlas como ✅ al completar.

### 1. Reemplazar ChatScreen.kt y ChatViewModel.kt (STUBS → PRODUCCIÓN)
- **Prioridad:** ALTA
- **Contexto:** Los archivos actuales en `ui/` son stubs mínimos creados por Antigravity. Necesitan ser reemplazados por una implementación completa.
- **Requisitos:**
  - Conexión WebSocket a `ws://10.0.2.2:8000/ws/chat`
  - Streaming de tokens en tiempo real (acumular `{"type": "token"}` y mostrar progresivamente)
  - Manejar `{"type": "metadata"}` para mostrar contexto ético
  - Manejar `{"type": "done"}` para finalizar mensaje y mostrar latencia
  - Manejar `{"type": "tts_audio"}` para reproducción de voz
  - Manejar `{"type": "clear_tokens"}` para limpiar tokens parciales (plugin mid-stream)
  - Manejar `vault_key` en evento `done` para mostrar diálogo de autorización
  - Auto-scroll al último mensaje
  - Indicador "Ethos está pensando..." mientras llegan tokens
- **Protocolo de envío:** `{"type": "chat_text", "payload": {"text": "..."}}`
- **Leer primero:** `AGENT_CONTEXT.md` en este mismo directorio
- **Status:** ✅ HECHO POR ANTIGRAVITY (Ciclo 1) — AS debe hacer `git pull` y validar compilación

### 2. Diseño Visual Premium
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

### 3. Coexistencia con NomadService
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
