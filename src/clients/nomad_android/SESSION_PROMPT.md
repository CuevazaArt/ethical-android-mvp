# 🎯 MISIÓN: Levantar la Nomad App y Conectarla al Kernel Ethos

> **Para pegar como primer mensaje en Android Studio.**
> Este prompt es el punto de coordinación entre **Antigravity (backend)** y **Android Studio (app)**.

---

## 🌐 ESTADO ACTUAL DEL SISTEMA (Confirmado por Antigravity)

| Componente | Estado | Detalles |
|---|---|---|
| **Ethos Server** | ✅ VIVO | `http://0.0.0.0:8000` · PID 11788 |
| **Ollama LLM** | ✅ VIVO | Modelos disponibles: `llama3.2:1b`, `gemma3`, `Llama3.1:8B`, `gemma4:31b` |
| **WebSocket Chat** | ✅ LISTO | `ws://10.0.2.2:8000/ws/chat` (desde emulador) |
| **WebSocket Nomad** | ✅ LISTO | `ws://10.0.2.2:8000/ws/nomad` (desde emulador) |

**El backend está vivo. Android Studio solo necesita compilar y correr la app.**

---

## 🎯 OBJETIVO DE ESTA SESIÓN

Lograr que la Nomad Android App:
1. **Compile y corra** en el emulador de Android Studio sin errores.
2. **Se conecte** al Ethos Kernel vía WebSocket a `/ws/chat`.
3. **Muestre una UI de chat funcional** donde el usuario pueda escribir y recibir respuestas de Ethos en tiempo real (streaming de tokens).
4. **Reproduzca el TTS** (voz de Ethos) cuando llegue `tts_audio`.

---

## 🔧 TU ROL: Android Studio

Tu trabajo es **exclusivamente el lado Android**. No modificas el backend Python.

### Paso 1 — Verifica que el proyecto compila

Abre el proyecto en: `src/clients/nomad_android/`

Verifica que `app/build.gradle.kts` tenga estas dependencias. Si falta alguna, agrégala:
```kotlin
implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
implementation("com.squareup.okhttp3:okhttp:4.12.0")
```

Haz **Build → Clean Project** y luego **Build → Make Project**. Reporta si hay errores.

---

### Paso 2 — Evalúa ChatViewModel.kt y ChatScreen.kt

Lee los archivos actuales en `ui/`:
- `ChatViewModel.kt` — Maneja el WebSocket y el estado de la conversación.
- `ChatScreen.kt` — UI de chat con burbujas de mensajes.

Estos son stubs básicos. Tu misión es **reemplazarlos con implementaciones completas**.

---

### Paso 3 — Implementa ChatViewModel.kt (producción)

El ViewModel debe:

```kotlin
// PROTOCOLO COMPLETO DE /ws/chat
// ─────────────────────────────────
// ENVIAR al servidor:
// {"type": "chat_text", "payload": {"text": "mensaje del usuario"}}
//
// RECIBIR del servidor — en este ORDEN:
// 1. {"type": "metadata", "context": "...", "signals": {...}}   → Estado ético
// 2. {"type": "token", "content": "palabra"}                    → Streaming (muchos)
// 3. {"type": "clear_tokens"}                                   → Borra tokens parciales (plugin)
// 4. {"type": "done", "message": "...", "blocked": false, "latency": {...}, "vault_key": null}
// 5. {"type": "tts_audio", "audio_b64": "BASE64", "text": "..."}
```

El ViewModel debe tener:
- `messages: SnapshotStateList<ChatMessage>` — lista reactiva de mensajes
- `streamingText: MutableState<String>` — texto que va llegando token a token
- `isThinking: MutableState<Boolean>` — true mientras llegan tokens
- `ethicsContext: MutableState<String>` — el campo `context` del evento `metadata`
- `fun sendMessage(text: String)` — envía al WebSocket
- Reconexión automática con delay de 3s si el socket falla

---

### Paso 4 — Implementa ChatScreen.kt (producción)

La UI debe tener estas secciones:

```
┌──────────────────────────────────┐
│  🟢 Ethos Kernel    [Badge ético]│  ← TopBar oscura
├──────────────────────────────────┤
│                                  │
│  [Burbuja usuario] ──────────█   │  ← Alineada a la derecha
│                                  │
│  █────── [Burbuja Ethos]         │  ← Alineada a la izquierda
│                                  │
│  Ethos está pensando...  ░░░     │  ← Animación pulsante (isThinking)
│                                  │
├──────────────────────────────────┤
│  [  Escribe a Ethos...  ] [►]   │  ← Input + Send
└──────────────────────────────────┘
```

**Paleta de colores obligatoria (dark cyberpunk):**
```kotlin
val BgPrimary    = Color(0xFF0D1117)  // Fondo principal
val BgSurface    = Color(0xFF161B22)  // Superficies/cards
val BgBorder     = Color(0xFF21262D)  // Bordes
val AccentGreen  = Color(0xFF3FB950)  // Verde Ethos (mensajes Ethos)
val AccentBlue   = Color(0xFF58A6FF)  // Azul acento (usuario)
val AccentGold   = Color(0xFFD29922)  // Dorado warning
val AccentRed    = Color(0xFFF85149)  // Rojo peligro (mensajes bloqueados)
val TextPrimary  = Color(0xFFE6EDF3)  // Texto principal
val TextSecondary= Color(0xFF8B949E)  // Texto secundario
```

**Comportamiento de burbujas:**
- Mensajes de usuario: fondo `AccentBlue` tenue, alineación derecha
- Mensajes de Ethos: fondo `BgSurface` con borde `AccentGreen`, alineación izquierda
- Mensajes bloqueados (safety): borde `AccentRed`, ícono ⚠️
- Auto-scroll al último mensaje siempre

---

### Paso 5 — Corre en el Emulador

1. Selecciona un emulador con API 26+ (mínimo que soporta el proyecto).
2. Corre la app.
3. El servidor ya está corriendo en tu PC en el puerto 8000.
4. El emulador llega a tu PC usando la IP especial `10.0.2.2`.

**Para verificar conectividad antes de correr la app:**
```bash
# Desde una terminal de Android Studio o adb shell:
adb shell curl http://10.0.2.2:8000/api/status
# Debe devolver JSON con {"status": "online", ...}
```

---

### Paso 6 — Prueba funcional

Una vez corriendo, prueba en este orden:
1. Escribe "Hola" → debe aparecer respuesta de Ethos con streaming.
2. Escribe "¿Qué hora es?" → debe usar el plugin Time y responder.
3. Escribe algo agresivo → debe ser interceptado por el safety gate.

---

### Paso 7 — Reporta en SYNC.md

Cuando termines (o si encuentras un bloqueante), actualiza la sección `📥 REPORTES` en:
`src/clients/nomad_android/SYNC.md`

Usa este template:
```markdown
### 2026-04-26 — ChatScreen/ViewModel implementados
- **Archivos modificados:** ui/ChatScreen.kt, ui/ChatViewModel.kt
- **Compila:** ✅
- **Problemas encontrados:** [o "ninguno"]
- **Necesito de Antigravity:** [cambio en backend / "nada"]
```

---

## 🚫 REGLAS ABSOLUTAS

1. **NO toques el backend Python** — el servidor está corriendo y funciona.
2. **NO toques** `NomadService.kt` — ya funciona, no lo rompas.
3. **NO toques** `network/MeshClient.kt` — está en ESTASIS.
4. **Mantén el header BSL 1.1** en todos los archivos Kotlin:
   ```kotlin
   // Copyright 2026 Juan Cuevaz / Mos Ex Machina
   // Licensed under the Business Source License 1.1
   ```
5. **Un archivo = un concepto**. No dupliques.

---

## 📡 COORDINACIÓN CON ANTIGRAVITY

Antigravity (el agente del IDE de backend) ya levantó el servidor y está monitoreando.
Si necesitas que Antigravity:
- Cambie algo en el protocolo WebSocket → escríbelo en `SYNC.md` bajo `📥`
- Reinicie el servidor → escríbelo en `SYNC.md`
- Agregue un endpoint de prueba → escríbelo en `SYNC.md`

Antigravity lee `SYNC.md` en cada ciclo y responde.

---

## 🗺️ MAPA MENTAL (una sola imagen)

```
Tu PC (Windows)
├── Ollama: llama3.2:1b @ :11434  ←──────────────────┐
└── Ethos Server: FastAPI @ :8000                     │
    ├── /ws/chat ◄──────── ChatViewModel.kt           │ LLM inference
    └── /ws/nomad ◄─────── NomadService.kt            │
                                               Ethos Core (Python)
Android Emulator
└── Nomad App (com.ethos.nomad)
    ├── MainActivity.kt → renderiza ChatScreen
    ├── ChatScreen.kt → UI de chat (TU OBJETIVO)
    ├── ChatViewModel.kt → WebSocket /ws/chat (TU OBJETIVO)
    └── NomadService.kt (background) → WebSocket /ws/nomad
```
