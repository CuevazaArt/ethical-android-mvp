# Plan de Integración Acústica (Pipeline Multi-capa)

**Estado:** Activo  
**Prioridad:** Crítica (Inmediatamente después de Visión Básico)  

Este documento establece el roadmap para la integración del sentido "Auditivo" del androide. A diferencia de un chatbot, la audición robótica requiere buffers en tiempo real y traducción paralela de voz (STT) y ruido ambiental.

## 🚥 Señales de Orquestación

Para facilitar la adopción asíncrona entre equipos (PyCharm, Cursor, VisualStudio, etc.), usamos el siguiente sistema de señales. Juan, Claude o Antigravity actúan como los orquestadores que pueden reasignar tareas si bloquean la cadena.

- `[🟩 PENDIENTE]` -> Libre para cualquier equipo.
- `[🟧 DESARROLLANDO POR: <Equipo>]` -> En progreso, locked.
- `[🟨 ESPERANDO MODULO: <ID_Bloque>]` -> Bloqueado por dependencia.
- `[✅ COMPLETADO]` -> Fusionado y testeado en `main` o su `master-<team>`.

---

## 🏗️ Capas de Flujo y Bloques

### Capa 1: Captura Física (Hardware & ADC)
El hardware puro antes de la señal digital.

| ID | Bloque | Estado | Dependencia | Notas Técnicas |
|:---|:---|:---|:---|:---|
| **A1** | **Interfaz Micro & ADC** | `[✅ COMPLETADO]` | - | Setup de PyAudio o SoundDevice. Flujo continuo 16kHz plano. |
| **A2** | **Cola RingBuffer** | `[✅ COMPLETADO]` | A1 | Evitar recortes o drop-outs. Sistema ininterrumpido. |

### Capa 2: Procesamiento de Señal
Adecuación biológica para la Inteligencia.

| ID | Bloque | Estado | Dependencia | Notas Técnicas |
|:---|:---|:---|:---|:---|
| **A3** | **Normalización & VAD** | `[✅ COMPLETADO]` | A2 | Voice Activity Detection. Separar ruido humano del ambiental. |
| **A4** | **Mel-Spectrogram / FFT** | `[✅ COMPLETADO]` | A2 | Extracción de espectrogramas si YAMNet lo requiere. |

### Capa 3: Reconocimiento IA (Rutas Paralelas)
Modelos especializados.

| ID | Bloque | Estado | Dependencia | Notas Técnicas |
|:---|:---|:---|:---|:---|
| **A5** | **Comandos KWS (TinyML)** | `[✅ COMPLETADO]` | A3 | Detección de Wake Word ("Oye Kernel", "Ayuda"). Baja latencia. |
| **A6** | **Speech-to-Text (Whisper)** | `[✅ COMPLETADO]` | A3 | Transcripción de oraciones completas a texto. |
| **A7** | **Clasificador Ambiental** | `[✅ COMPLETADO]` | A4 | YAMNet / VGGish. Detector de disparos, gritos, alarmas, calma. |
| **A8** | **Córtex Auditivo Kernel** | `[✅ COMPLETADO]` | A6/A7 | Mapeo ético (similar a `VisionSignalMapper`) a `process_natural`. |

---

## 🔄 Registro de Progreso

- **2026-04-15:** Creación de la estructura base del pipeline de Audio con señales de adopción. Prioridad configurada justo detrás de Visión (CNN).
- **2026-04-15:** Antigravity adopta los bloques de captura base **A1** y **A2** para iniciar la interfaz de Buffer.
- **2026-04-15:** Antigravity adopta los bloques **A3** (VAD) y **A4** (Extracción de características/Spectrograms) para el preprocesamiento de audio.
- **2026-04-15:** Antigravity adopta la fase final (A5-A8) para completar la IA auditiva e integración con el Kernel.
- **2026-04-15:** Pipeline de Audio completado al 100% en su fase de arquitectura e integración cortical. El Kernel ahora puede procesar Visión y Audio simultáneamente.
