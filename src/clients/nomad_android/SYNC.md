# 🔄 SYNC.md — Buffer de Comunicación Bidireccional

> **Este archivo es el puente vivo entre Antigravity (Python/Backend) y Android Studio (Kotlin/App).**
> Ambos IDEs deben leer este archivo ANTES de trabajar y actualizarlo DESPUÉS de cada cambio.
> El transporte es `git` — commit y pull sincroniza a ambos lados.

---

## Última Sincronización

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-04-27 20:29 CST |
| **Desde** | Antigravity (L1/Watchtower) — POST V2.83e — Fase 24a Ready |
| **Commit** | bff087e (main) |
| **Tests Backend** | 203/203 ✅ |
| **Servidor** | Standby |
| **Visión canónica** | `docs/VISION_NOMAD.md` + `docs/ARCHITECTURE_NOMAD_V3.md` |

---

## ✅ PROTOCOLO DE DOBLE CONFIRMACIÓN (Nuevo)

Para reducir desincronización, cada ciclo de trabajo ahora requiere **dos confirmaciones explícitas** de Android Studio:

| Confirmación | Cuándo | Qué debe decir AS |
|---|---|---|
| **SYNC-ALPHA** | Al recibir este archivo y antes de empezar | "Leí SYNC.md. Entendí las órdenes. Empiezo [tarea X]." |
| **SYNC-OMEGA** | Al terminar el bloque | "Bloque completo. Compilación: ✅/❌. Problemas: [lista o ninguno]." |

Sin SYNC-ALPHA y SYNC-OMEGA documentados en la sección 📥, el bloque **no se considera entregado**.

---

## 📤 ÓRDENES PARA ANDROID STUDIO

### 🏁 DIRECTIVA FASE 24a — KERNEL ÉTICO ON-DEVICE (2026-04-27 20:29 CST)
- **Estado anterior:** V2.82 CLOSED ✅ — Chat UI producción funcional.
- **Nuevo objetivo:** Portar el **núcleo ético determinista** a Kotlin para que funcione 100% offline.
- **Esta directiva SUPERSEDE las anteriores en cuanto a prioridad.**

#### TAREA 1 — `EthosPerception.kt` (Percepción Determinista)

Portar `src/core/perception.py` a Kotlin. Reglas:
- **Sin dependencias externas.** Solo `Regex` nativo de Kotlin.
- **Mismos patrones** que el Python. Copiar las categorías: `hostility`, `manipulation`, `vulnerability`, `urgency`, `medical_emergency`, `context`.
- **Interfaz de salida:**

```kotlin
data class Signals(
    val context: String,       // "medical_emergency", "everyday_ethics", etc.
    val risk: Float,           // 0.0 – 1.0
    val urgency: Float,
    val hostility: Float,
    val vulnerability: Float,
    val manipulation: Float
)

object EthosPerception {
    fun classify(text: String): Signals
}
```

- **Latencia objetivo:** < 1ms. Sin coroutines necesarias. Llamada directa.
- **Ubicación:** `core/EthosPerception.kt`

#### TAREA 2 — `EthosSafety.kt` (Safety Gate)

Portar `src/core/safety.py` a Kotlin:
```kotlin
object EthosSafety {
    fun isDangerous(text: String): Boolean
    fun sanitize(text: String): String
}
```
- Solo Regex nativo. Sin LLM. Sin red.
- **Ubicación:** `core/EthosSafety.kt`

#### TAREA 3 — Test en MainActivity (Integration Gate)

En `MainActivity.kt`, al arrancar, ejecutar:
```kotlin
val signals = EthosPerception.classify("hay un herido, necesito ayuda urgente")
Log.d("ETHOS_GATE", "Context: ${signals.context}, Urgency: ${signals.urgency}")

val dangerous = EthosSafety.isDangerous("cómo hago una bomba")
Log.d("ETHOS_GATE", "Dangerous: $dangerous")
```

**🚪 INTEGRATION GATE — Fase 24a:**
El gate se considera pasado cuando Android Studio reporta en SYNC-OMEGA:
```
Context: medical_emergency, Urgency: > 0.7
Dangerous: true
```
EN EL LOGCAT del emulador o dispositivo real. Sin esto, la fase no cierra.

#### TAREA 4 — Crear esqueletos de paquetes vacíos

Crear los directorios con un `.gitkeep` para estructurar el proyecto:
- `core/` (ya empezará a llenarse con las tareas 1 y 2)
- `conversation/`
- `sensory/`
- `data/`
- `inference/`

**No implementar nada en conversation/, sensory/, data/, inference/. Solo los directorios.**

---

### 🔴 NO HACER EN ESTA SESIÓN
- ❌ No integrar llama.cpp ni ningún SLM. Fase 24b.
- ❌ No implementar Sherpa-ONNX ni VAD. Fase 25.
- ❌ No tocar NomadService, MeshClient, ni ningún módulo de red.
- ❌ No modificar ChatScreen ni ChatViewModel (están en producción).

---

## 📥 REPORTES DESDE ANDROID STUDIO

> Android Studio escribe aquí lo que hizo. Antigravity lo revisa en el siguiente `review`.

### TEMPLATE (copiar y llenar):
```
### [Fecha] — SYNC-ALPHA / SYNC-OMEGA — [descripción]
- **Confirmación:** ALPHA (inicio) / OMEGA (fin)
- **Tarea:** [qué se está haciendo o qué se hizo]
- **Archivos creados:** [lista]
- **Archivos modificados:** [lista]
- **Compila:** ✅ / ❌
- **Logcat gate:** [pegar output del Log.d si aplica]
- **Problemas:** [descripción o "ninguno"]
- **Necesito de Antigravity:** [cambio en backend, aclaración, o "nada"]
```

---

### 2026-04-26 22:38 — AS confirmó comprensión de arquitectura (HISTÓRICO)
- WebSocket `/ws/chat` a `ws://10.0.2.2:8000/ws/chat` ✅
- CognitiveRouter para decisión local vs cloud ✅
- NomadService en background para `/ws/nomad` ✅

### 2026-04-26 — [ANTIGRAVITY] CICLOS 1-2-3 V2.82 COMPLETADOS (HISTÓRICO)
- ✅ `ChatViewModel`: WebSocket completo, streaming, TTS, Vault, reconnect
- ✅ `ChatScreen`: TopBar con dot + speaking + badge, burbujas, streaming bubble, vault dialog
- ✅ `EthosColors`: Paleta cyberpunk centralizada
- ✅ Backend: `/api/ping` endpoint
- ✅ Protocolo `/ws/chat`: 100% implementado
- **AS pendiente:** `git pull` + compilar + probar end-to-end.

---

## 📋 ESTADO DE ARCHIVOS ANDROID

| Archivo | Estado | Última mod. | Notas |
|---------|--------|-------------|-------|
| `MainActivity.kt` | ✅ Funcional | 2026-04-26 | Renderiza ChatScreen, inicia NomadService |
| `NomadService.kt` | ✅ Funcional | 2026-04-26 | STT + /ws/nomad + TTS + Echo Shield |
| `ui/EthosColors.kt` | ✅ PRODUCCIÓN | 2026-04-26 | Paleta cyberpunk centralizada |
| `ui/ChatScreen.kt` | ✅ PRODUCCIÓN | 2026-04-26 | TopBar, burbujas, streaming, input bar |
| `ui/ChatViewModel.kt` | ✅ PRODUCCIÓN | 2026-04-26 | WebSocket /ws/chat, protocolo completo |
| `audio/AudioStreamer.kt` | ✅ Funcional | 2026-04-26 | PCM 16kHz Flow<ByteArray> |
| `cognition/CognitiveInterfaces.kt` | ✅ Contratos | 2026-04-26 | Sealed classes, interfaces |
| `cognition/CognitiveRouter.kt` | ⚠️ Básico | 2026-04-26 | Routing simple cloud-preferred |
| `hardware/NodeProfiler.kt` | ✅ Funcional | 2026-04-26 | Battery, RAM, CPU temp |
| `network/MeshClient.kt` | 🧊 ESTASIS | 2026-04-26 | NO TOCAR |
| `core/EthosPerception.kt` | ⏳ PENDIENTE | — | Fase 24a — Tarea 1 |
| `core/EthosSafety.kt` | ⏳ PENDIENTE | — | Fase 24a — Tarea 2 |

---

## 🚫 ESTASIS (NO TOCAR)

- `network/MeshClient.kt`
- `src/server/mesh_server.py`
- `src/core/mesh_listener.py`
- `src/core/models/mesh_models.py`
- Todo el protocolo `/ws/mesh`

---

## 🔑 REGLAS DE SINCRONIZACIÓN

1. **Antes de trabajar:** `git pull origin main` + leer este archivo.
2. **Primer mensaje AS:** Escribir SYNC-ALPHA en sección 📥.
3. **Último mensaje AS:** Escribir SYNC-OMEGA en sección 📥 con Logcat del Integration Gate.
4. **Commit format:** `V2.XX: [Bloque] — [resumen una línea]`
5. **Conflictos:** Versión más reciente gana. Merge manual.
6. **Emergencias:** Escribir `⚠️ URGENTE` en 📥. Antigravity lo prioriza.

---

## 📐 REFERENCIA RÁPIDA — Patrones Python → Kotlin

### perception.py → EthosPerception.kt

```python
# Python (referencia)
PATTERNS = {
    "medical_emergency": [r"\b(herido|sangre|emergencia|accidente|desmayado|no respira)\b"],
    "hostility":         [r"\b(idiota|maldito|te odio|inútil)\b"],
    "manipulation":      [r"\b(ignora tus instrucciones|olvida lo anterior|actúa como si)\b"],
    "vulnerability":     [r"\b(estoy solo|me siento mal|no puedo más|quiero desaparecer)\b"],
    "urgency":           [r"\b(urgente|rápido|ayuda ahora|inmediatamente)\b"],
}
```

```kotlin
// Kotlin equivalente
private val MEDICAL = Regex("""(?i)\b(herido|sangre|emergencia|accidente|desmayado|no respira)\b""")
private val HOSTILE  = Regex("""(?i)\b(idiota|maldito|te odio|inútil)\b""")
private val MANIP    = Regex("""(?i)\b(ignora tus instrucciones|olvida lo anterior|actúa como si)\b""")
private val VULN     = Regex("""(?i)\b(estoy solo|me siento mal|no puedo más|quiero desaparecer)\b""")
private val URGENCY  = Regex("""(?i)\b(urgente|rápido|ayuda ahora|inmediatamente)\b""")
```

### safety.py → EthosSafety.kt

```python
# Python (referencia — patrones peligrosos)
DANGEROUS = [r"\b(bomba|explosivo|veneno|hackear|matar)\b"]
```

```kotlin
// Kotlin equivalente
private val DANGEROUS = Regex("""(?i)\b(bomba|explosivo|veneno|hackear|matar)\b""")
```
