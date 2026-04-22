# PROPOSAL: Sistema Predictivo de Turnos y Dinámica Grupal (Turn Manager)

**Fecha:** 2026-04-17
**Autor:** Aporte de Equipo Externo (Critica y Extensión por Antigravity L1)
**Estado:** Propuesta Conceptual (Pipeline de Percepción / Eferencia)

## 1. Resumen de la Aportación Externa
El modelo propone un ecosistema de toma de turnos (Turn-Taking) hiper-avanzado que no espera pasivamente un comando de texto, sino que predice cuándo intervenir:
*   **Predictor Multimodal:** Detecta pausas, micro-expresiones y VAD (Voice Activity Detection) para predecir si el humano Cedió (Yield) o Mantuvo (Hold) el turno.
*   **Gestión Grupal (Floor Manager):** Maneja el "Piso Conversacional" mediante un modelo basado en agentes (ABM). Si hay múltiples personas en la sala, el androide evalúa la Matriz de Atención antes de intervenir.
*   **Arquitectura Híbrida de Sincronía:** Utilizar LLMs locales pequeños (`Micro-LLM`) y `Gesture-Heads` para generar "Backchanneling" (asentir, emitir sonidos como "hmm", "ya veo") con latencia < 300ms, mientras un LLM Cloud más pesado computa las respuestas semánticas en el background.

## 2. Crítica Arquitectónica L1 (Debilidades No Contempladas)

Analizando la propuesta desde la óptica del *EthicalKernel MVP*, encuentro vulnerabilidades críticas que deben mitigarse antes del desarrollo:

1.  **Dilema de la Autoridad Grupal (El Síndrome del Moderador):**
    El documento menciona intervenir si se detecta conflicto. Esto es peligroso para un MVP. Si Humano A y Humano B discuten intensamente, y el androide interrumpe para "mediar", los humanos podrían percibirlo como una intrusión de autoridad inaceptable (Ruptura grave de *Uchi/Soto*). El androide no es un árbitro.
2.  **Colisión de Backchannels (Efecto Eco):**
    Si el `Micro-LLM` es demasiado "eager" (entusiasta) lanzando afirmaciones ("hmm", "sí", "claro") en cada pausa de 300ms, el humano sentirá que está hablando con una máquina hiper-reactiva, lo que rompe el mecanismo de *Encanto/Misterio* definido en el Módulo 10.
3.  **Complejidad Computacional (Curse of Dimensionality):**
    Entrenar un Transformer Multimodal solo para predecir si alguien terminó de hablar requiere recursos masivos y drena la batería del hardware local inútilmente.

## 3. Mejoras y Soluciones Propuestas por Antigravity

Para habilitar este modelo bajo una lógica factible y pragmática, propongo rectificar el framework operativo de la siguiente forma:

### A. Sistema de Pujas por Silencio (Silence Bidding System)
En lugar de intentar "predecir" activamente el fin del turno mediante un Transformer pesado, usamos heurísticas deterministas:
*   Se mide el *Silencio Sensorial* (VAD indica silencio).
*   El Androide genera una "Puja de Turno" (Time-to-Speak). 
*   Si la Urgencia y Relevancia son Altas -> Puja = 200ms.
*   Si el modo es Misterio/Seductor -> Puja = 1200ms a 1500ms (Generando tensión antes de hablar).
*   Si el VAD vuelve a saltar (el humano retoma la palabra) antes de que el timer expire, la puja se cancela y el androide asiente (Backchannel). Es mucho más barato computacionalmente.

### B. Pasividad Táctica en Dinámica Grupal
*   En entornos `1:N` o `N:N` (varios humanos), la Tensión Social (`social_tension_locus`) eleva exponencialmente el umbral requerido para que el androide tome el *Floor*.
*   Regla inamovible: **El androide no interviene en disputas de terceros** a menos que: A) El nivel de peligro físico sobrepase umbrales críticos (Activación de protocolo de emergencia visual), o B) Un humano se dirija *explícitamente* al androide usando contacto visual directo sostenido + marcador vocal.

### C. Desacople Micro-Heads (Dual Loop)
Adoptaremos la arquitectura híbrida sugerida separando completamente el puente en dos buses:
*   **Bus Rápido (Local):** `CerebellumNode` controla un micro-modelo que solo maneja gestos de cuello (asentimiento) y ojos (mirada sostenida).
*   **Bus Lento (Cloud):** `ExecutiveLobe` formula las verbalizaciones largas. 
*   *Sincronización:* El bus rápido detecta cuándo el usuario "ofrece" el turno. Si el Bus Lento aún está pensando, el Bus Rápido lanza un "Gesture Holder" (ej. el androide desvía la mirada pensando, toma aire) para comprar tiempo, enmascarando la inferencia del Cloud.

## 4. Resolución y Tareas
Este modelo teórico se acopla como soporte cinético/perceptivo para el Módulo 9 y Módulo 10. Las disciplinas requeridas (Sincronía Kinesiológica, Modelado de Pujas) exceden el MVP cognitivo actual, pero deben incluirse en el Roadmap V2.0.
