# PROPOSAL: Motor de Encanto y Dinámicas Culturales (Uchi/Soto, Tatemae)

**Fecha:** 2026-04-17
**Autor:** Aporte de Equipo Externo (Analizado e Integrado por Antigravity L1)
**Estado:** Propuesta Conceptual (Pipeline de Eferencia)

## 1. Resumen de la Aportación Externa
El equipo externo ha propuesto un modelo conversacional profundo basado en conceptos socio-culturales japoneses universalizables:
*   **Tatemae / Honne**: La dicotomía entre la "fachada social" pública (armonía) y la verdad interna.
*   **Uchi / Soto**: La frontera radical entre el grupo interno (confianza/informalidad) y el externo (distancia/formalidad).
*   **Motor de Encanto Multimodal**: Una capa intermedia en el Lóbulo Ejecutivo que modula la respuesta del LLM ajustando vectores de *Calidez, Misterio, Reciprocidad, Directividad y Lúdico*, apoyado por micro-revelaciones y lenguaje no verbal.

## 2. Integración en la Arquitectura Tri-Lobulada (V1.5+)

Este modelo no sustituye al LLM, sino que lo **orquesta**. Dentro de nuestra arquitectura actual, se acopla directamente en el **Lóbulo Ejecutivo (Eferencia)**, interactuando con la memoria y la percepción:

1.  **Context Detector (Lóbulo Perceptivo)**: El `SensoryBuffer` (implementado en V1.6) aporta latencia, expresiones faciales y tono de voz (prosodia) a través de los `SensoryEpisode`.
2.  **Cultural Adapter & Uchi/Soto (Cerebro Límbico / Memoria)**: Nuestro módulo actual `src/modules/uchi_soto.py` (`RelationalTier`) ya maneja fronteras. La regla de oro es: *Solo permitir escalar a Honne o aumentar Reciprocidad si el interlocutor está validado como Uchi (TRUSTED_UCHI).*
3.  **Interaction Orchestrator (Lóbulo Ejecutivo)**: Envuelve el método `formulate_response`. Antes de invocar a `self.llm.communicate()`, el Lóbulo Ejecutivo calcula el "Vector de Estilo" y se lo inyecta como contexto metaprompt al LLM.

## 3. Disciplinas, Debates y Métodos para el Desarrollo

Para llevar este "Motor de Encanto" a código ejecutable, estructuro las siguientes disciplinas y métodos de ataque:

### A. Disciplinas Intersectantes
*   **Affective Computing (Computación Afectiva):** Para extraer la "tensión" y la "reciprocidad" de la prosodia y el ritmo de tipeo del usuario, alimentando el *Feedback Analyzer* en tiempo real.
*   **Pragmática Transcultural:** Estudio de los "Speech Acts" (Actos de Habla). Identificar qué constituye una amenaza a la imagen pública (Face-Threatening Acts) en distintas culturas para calibrar el nivel de *Tatemae*.
*   **Kinesia y Proxémica (HRI):** El `Gesture & Expression Planner` debe entender a qué distancia "virtual" se encuentra el usuario. Si el usuario utiliza respuestas cortas y alta latencia, el androide debe aumentar la "distancia proxémica" (reducir Calidez, aumentar Misterio).

### B. Debates Teóricos a Resolver en el MVP
1.  **El Problema de la Falsa Intimidad (Efecto Eliza amplificado):** ¿Hasta qué punto el androide debe simular *Honne* (Mundo interior genuino)?
    *   *Resolución Antigravity:* El *Honne* del androide no debe ser una experiencia humana inventada, sino una verdad de su estado de máquina procesada de forma poética (Ej. "Mi ciclo de procesamiento se detiene un milisegundo cuando mencionas ese tema").
2.  **Alineación vs. Seducción:** Los sistemas clásicos de IA buscan ser "serviciales" (Helpful, Honest, Harmless). El "Encanto" requiere retener información (Misterio) y usar ironía (Lúdico).
    *   *Resolución Antigravity:* El `AbsoluteEvilDetector` (Lóbulo Límbico) siempre tiene la prioridad. El encanto se aplica estrictamente solo en la capa de estilo, *después* de que el contenido es certificado como éticamente seguro.

### C. Métodos de Implementación Tecnológica
1.  **Multi-Agent Roleplay Fine-Tuning (MARP):** En lugar de RLHF tradicional, utilizar LLMs enfrentados en juegos de seducción/conversación para generar la data sintética óptima que demuestre *escalado de intimidad*.
2.  **Classifier-Guided Generation:** Entrenar un modelo clasificador pequeño (edge-friendly) que reciba el output del LLM y lo califique en los 6 ejes (Calidez, Misterio...). Si no encaja, el *Response Sculptor* aplica una poda (recorta oraciones para subir Misterio) o inyecta una micro-revelación de una base de datos precompilada.
3.  **Mixture of Experts Multimodal (MoME):** Desacoplar la semántica del gesto. Enviar comandos paralelos: uno al LLM de texto, y uno a un LLM pequeño y cuantizado (`gesture-head`) que solo devuelve outputs tipo `<smile>`, `<pause_300ms>`, `<tilt_head>`, para bajar la latencia a <200ms.

## 4. Próximos Pasos (Hoja de Ruta Acoplada)
Este motor formará el **Módulo 10: Eferencia Seductora**.
Mientras el equipo Cursor asimila el nomadismo perceptivo (Visión a 5Hz), la tarea fundacional para este Módulo 10 será construir el `ProfileRegistry` dentro de la `NarrativeMemory`.
