# Proposal: Pilar de la Mente (Arquitectura Cognitiva y Narrativa Sofisticada)

## Contexto
El modelo actual de memoria del Androide Ético está fragmentado entre ciclos límite de retención, EMA básicos y asignación relacional léxica. Para conferirle propiedades orgánicas, este plan propone entrelazar las mecánicas a través de sub-bloques, niveles vectoriales y consolidación de identidad.

## 1. Topología de la Memoria (Registro y Almacenaje)
- **Tier 1 (Memoria de Trabajo / Corto Plazo)**: Buffer efímero en memoria RAM gestionando transcripciones y métricas a cortísimo plazo (`working_memory.py`). Transmite estado táctico.
- **Tier 2 (Memoria Episódica Sensorial / Medio Plazo)**: ✅ **ENTREGADO** (SQLite persistence in `narrative_storage.py`). Se guarda el ciclo semántico y el `Affect_PAD`. Soporta búsqueda por resonancia (`find_by_resonance`).
- **Tier 3 (Consolidación de Identidad / Filosofía)**: El LLM compacta episodios vectoriales viejos destilando "lecciones existenciales" en `existence_digest` (`narrative_identity.py` y `existential_serialization.py`).

## 2. Mecánica del Recuerdo (Retrieve & Access)
El androide no busca linealmente; "recuerda por resonancia". 
- Picos altos de estrés emocional (alto `hostility` o estrés de `sigma`) fuerzan un muestreo (RAG Vectorial) hacia eventos donde se padeció el mismo perfil de perturbación.
- Se integra aquí **Uchi-Soto**: el filtro relacional determina qué acceso se tiene a los bloques profundos. Al interactuar con el *OWNER*, la retención fluye hasta la memoria Tier 3; un *SOTO_HOSTIL* interactúa exclusivamente contra el Tier 1 (buffer) bajo barreras defensivas estrictas.

## 3. Mapas de Personas y Perfiles Activos
- Las personas conocidas no son simples identificadores, sino "Topologías de Riesgo e Intimidad" modeladas en `InteractionProfile`. 
- El cruce entre el puntaje de Confianza (`TrustCircle`) y la racha de hostilidad computada por la deducción cognitiva dicta qué tan dócil es el droide o si levanta el muro dialéctico.

## 4. Estrategia y Autonomía (Metaplanes)
- Interacción `metaplan_registry.py`: Los propósitos de largo aliento configurados por el dueño se almacenan como vectores éticos a perseguir pasivamente.
- La identidad en transición (vgr., si baja el `civic_lean` repetidas veces tras el trauma del Androide) altera la ponderación de `DriveIntent`. Si el historial enseña cuidado (`care-oriented`), los metaplanes que exijan confrontación pierden latencia automática, cediendo autonomía sobre la directriz humana.

## Compartimentación
Todo el componente evaluativo RAG (Memoria Semántica y Episódica) estará fuertemente "ensandboxado" del detector **Absolute Evil**. El mal absoluto sigue cortando el flujo por hardware sin depender de asimilación LLM profunda, salvaguardando contra manipulaciones adversarias.
