# Revisión Técnica de Aportes Externos — 2026-04-27

> **Autor:** L1 (Watchtower / Antigravity)
> **Fuente:** Colaborador externo vía chat. Tres bloques de información recibidos.
> **Propósito:** Digerir, criticar e integrar donde ayude. No invasión al flujo actual.

---

## I. Clasificación del Aporte

Se recibieron tres bloques temáticos:

| # | Tema | Tipo | Valor para Ethos |
|---|-------|------|-----------------|
| 1 | Análisis Meta AI WhatsApp (expandido) | Investigación UX/Persona | **ALTO** — Ya integrado parcialmente en V2.84b |
| 2 | Git multi-cuenta en misma PC | Ops/DevOps | **MEDIO** — Útil para L0, no toca código |
| 3 | Sugerencias de tecnologías open-source | Arquitectura/Roadmap | **ALTO** — Requiere análisis fino |

---

## II. Crítica al Aporte de Meta WhatsApp (Bloque 1)

### Lo que aporta bien
- La taxonomía de los 8 factores (framing, persona layer, micro-turnos, etc.) es sólida y accionable.
- La tabla comparativa `Meta AI vs LLM promedio` es directamente utilizable como spec para nuestro `PersonalityConfig`.
- La observación sobre el **framing psicológico** (contacto vs herramienta) es la más valiosa: confirma que nuestra decisión de poner a Ethos en un **chat de WhatsApp-style** en lugar de una interfaz técnica fue correcta desde V2.82.

### Lo que exagera o simplifica
- "Entrenamiento con datos de redes sociales" — Meta tiene un dataset único, pero nosotros no necesitamos replicar eso. Nuestro modelo local (llama3.2:1b) es demasiado pequeño para absorber estilo vía fine-tuning. La solución correcta para nosotros es **prompt engineering agresivo** (ya aplicado en V2.84b) y un futuro `PersonalityConfig.kt` que aplique reglas deterministas sobre la salida del LLM.
- "Menos restricciones de tono" — Peligroso tomarlo al pie de la letra. Ethos tiene un kernel ético por diseño. No podemos sacrificar seguridad por calidez. La solución es: **ser cálido DENTRO de los límites éticos**, no relajar los límites.

### Lo que ya integramos
- **V2.84b (este bloque):** Se modificó `RESPONSE_PROMPT` en `chat.py` para inyectar el estilo "contacto de WhatsApp" directamente al system prompt. Instrucciones de micro-turnos, brevedad y tono humano ya están activas.

### Lo que queda pendiente (Fase 25)
- `PersonalityConfig.kt` — Archivo Kotlin que contendrá las reglas del persona layer como constantes tipadas.
- `ConversationState.kt` — Máquina de estados para controlar el flujo de turn-taking y micro-turnos.
- Ambos vivirán en `src/clients/nomad_android/app/src/main/java/com/ethos/nomad/core/`.

---

## III. Crítica al Aporte de Git Multi-Cuenta (Bloque 2)

### Veredicto: CORRECTO pero fuera de scope de código.

La guía SSH multi-cuenta es técnicamente precisa. Las recomendaciones son estándar:
- 1 clave SSH por cuenta → `~/.ssh/config` con `Host` aliases → `git config --local` por repo.

**Acción para L0:** Si necesitas trabajar con otro repo de otra cuenta de GitHub al mismo tiempo que Ethos, sigue la guía del aporte. No hay impacto en el código del proyecto.

**Nota operativa:** El problema de credenciales que tuvimos antes en esta sesión (el `git push` fallando) se resolvió limpiando el Windows Credential Manager. Si L0 adopta SSH keys en lugar de HTTPS, ese problema desaparece permanentemente.

---

## IV. Crítica al Aporte de Tecnologías Open-Source (Bloque 3)

Este es el bloque más denso. Analizo cada sugerencia contra la arquitectura real del proyecto.

### ✅ INTEGRAR (encajan con la arquitectura actual o el roadmap)

| Tecnología | Área | Por qué sí | Fase de integración |
|------------|------|------------|-------------------|
| **Sherpa-ONNX** | Voz / STT | Ya está en el roadmap (Fase 25). Reemplaza el `SpeechRecognizer` nativo que causa el beep molesto. Motor de STT silencioso, local, sin dependencia de Google. | **Fase 25** |
| **Silero VAD** | Voz / Wake-word | Complementa a Sherpa. Detector de actividad vocal ultraligero (~2MB). Permite activar STT solo cuando hay voz real, ahorrando batería y CPU. | **Fase 25** |
| **Whisper.cpp** | Voz / STT | Alternativa a Sherpa-ONNX. Más pesado pero más preciso. Considerarlo como fallback si Sherpa no da la calidad suficiente en español. | **Fase 25 (alternativa)** |
| **FAISS** | Memoria | Nuestra memoria semántica actual usa `sentence-transformers` + búsqueda lineal. FAISS aceleraría la búsqueda vectorial cuando la memoria crezca a miles de episodios. | **Fase 24b (servidor)** |
| **MediaPipe** | Visión | Ya tenemos OpenCV para detección básica de rostros. MediaPipe añade pose, manos y landmarks faciales. Útil para el "contexto social" de Fase 25. Corre en Android nativo. | **Fase 25+** |
| **OpenTelemetry** | Observabilidad | Tenemos telemetría artesanal en `app.py`. OpenTelemetry la estandarizaría. Pero solo cuando el sistema tenga más de un nodo. | **Fase 26+** |

### ⚠️ CONSIDERAR CON RESERVAS

| Tecnología | Área | Análisis |
|------------|------|----------|
| **Qdrant** | Memoria vectorial | Es un server de vectores. Nuestro proyecto busca ser **local-first**. SQLite + FAISS es más apropiado que levantar un servicio extra. Solo útil si escalamos a Modo 2 (Centinela). |
| **Coqui TTS** | Voz / TTS | Ya usamos `edge-tts` que es gratis, rápido y de alta calidad (DaliaNeural). Coqui requiere entrenar voces y consume más recursos. Solo útil si queremos una voz 100% propia y única para Ethos. |
| **TensorFlow Lite** | Inferencia Android | Competidor de `llama.cpp` para inferencia on-device. TFLite es más maduro en Android pero los modelos de lenguaje modernos corren mejor en llama.cpp/GGUF. |
| **OPA (Open Policy Agent)** | Seguridad | Interesante conceptualmente — un motor de políticas declarativo. Pero nuestro kernel ético ya ES un motor de políticas (Perception + Ethics + CBR). OPA sería redundante a menos que necesitemos políticas de infraestructura (no de ética conversacional). |

### ❌ NO INTEGRAR (no encajan o son prematuros)

| Tecnología | Razón de rechazo |
|------------|-----------------|
| **YOLOv8 / YOLO-NAS** | Detección de objetos en tiempo real consume demasiada batería y CPU para un teléfono en producción. La Visión Nómada dice explícitamente: "usar APIs cuando haya red, stubs cuando no". No es prioridad. |
| **PettingZoo / Gymnasium** | Simulación multi-agente. Elegante académicamente, pero Ethos es un agente individual, no un enjambre competitivo. No hay caso de uso concreto hasta Modo 3 (Enjambre), que está en Fase 27+. |
| **CARLA** | Simulación urbana pesada (requiere GPU dedicada). Completamente fuera de scope para un teléfono en la solapa. |
| **ROS 2** | Estándar de robótica. Solo tiene sentido si Ethos habita un chasis robótico físico. Aspiracional pero no para los próximos 6 meses. |
| **HashiCorp Vault** | Overkill. Nuestro `SecureVault` en `vault.py` es suficiente para secretos de un solo usuario. HashiCorp Vault es para infraestructura enterprise multi-tenant. |
| **SentenceTransformers** | ¡Ya lo usamos! (`all-MiniLM-L6-v2` en `memory.py`). No es una sugerencia nueva. |

---

## V. Impacto en el Roadmap

Tras analizar todo, el roadmap NO necesita rediseño. Las tecnologías que aportan valor ya están alineadas con las fases existentes. Solo añado anotaciones:

### Roadmap Anotado

```
Fase 24a — Kernel Ético On-Device (ACTUAL)
  → Sin cambios. Perception + Safety en Kotlin puro (Regex).
  → GATE: EthosPerception.kt en emulador.

Fase 24b — Persistencia + SLM
  → Sin cambios.
  → NOTA: Considerar FAISS para la memoria si los episodios superan 500.

Fase 25 — Voice Pipeline  ← PRINCIPAL BENEFICIARIO DEL APORTE
  → Sherpa-ONNX como STT local (reemplaza SpeechRecognizer nativo)
  → Silero VAD como detector de voz (wake-word trigger)
  → PersonalityConfig.kt (persona layer del análisis Meta)
  → ConversationState.kt (micro-turnos del análisis Meta)
  → GATE: "Ethos, ¿qué hora es?" por voz sin beeps.

Fase 25+ — Proactividad y Sensores
  → MediaPipe como upgrade de OpenCV para visión contextual.
  → GATE: Ethos comenta sobre el entorno.

Fase 26+ — Expansión
  → OpenTelemetry si hay multi-nodo.
  → Vault biométrico nativo Android.
```

---

## VI. Conclusión

El aporte externo es valioso como **exploración de posibilidades**, pero requiere filtrado severo contra nuestra realidad:

1. **Somos local-first.** Cualquier tecnología que requiera un servidor adicional o conexión constante se descarta o posterga.
2. **Somos battery-conscious.** Cualquier cosa que corra "siempre" (YOLO, CARLA) quema batería y mata la experiencia nómada.
3. **Somos un individuo, no un enjambre.** Las herramientas multi-agente son prematuras hasta que el mono-nodo sea impecable.
4. **Lo más valioso del aporte no es tecnológico, es psicológico.** La investigación sobre Meta WhatsApp nos confirma que el tono y el framing importan más que el modelo. Eso ya lo estamos aplicando.

> *"No necesitamos 20 tecnologías. Necesitamos 3 bien integradas: un STT silencioso (Sherpa), una memoria rápida (FAISS), y un persona layer que haga sentir a Ethos como un amigo, no como una herramienta."*
