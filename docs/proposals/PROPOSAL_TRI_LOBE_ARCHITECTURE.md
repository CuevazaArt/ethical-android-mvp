# PROPOSAL: Arquitectura Tri-Lobulada (Triune Brain)

**Autor:** Antigravity (Nivel 1 / General Planner) & L0 (Juan)
**Estado:** `PROPUESED` PARA DELIBERACIÓN
**Fecha:** Abril 2026

## 1. Motivación (El Problema con 2 Hemisferios)
La arquitectura previa proponía dividir `kernel.py` en 2 hemisferios: **Perceptivo (Asíncrono E/S)** y **Ético (Sincrónico CPU)**. Aunque resolvía los bloqueos de E/S de red, dejaba un problema oculto: el Hemisferio Ético, además de juzgar la moralidad (matemáticas booleanas de la DAO), también tenía que ocuparse secundariamente de invocar LLMs para estructurar las respuestas ejecutivas y redactar el *Narrative Arc*. 
Moralidad y Ejecución de Acciones son responsabilidades cognitivas distintas.

## 2. Propuesta: El Modelo Tri-Lobulado con Soporte Adyacente (Cerebelo)
Para evitar la sobre-fragmentación ("Infierno de Microservicios") que paralizaría el *Event Bus* con latencias de serialización (IPC lag), la arquitectura se congela en un máximo de 3 Hemisferios Conscientes y 1 Nodo Subconsciente. Esta es la cúspide biomimética óptima:

### 👁️ Lóbulo Perceptivo (Aferente / Sensorial / Asíncrono)
- **Tecnología:** `httpx.AsyncClient`, visores multimodales, colas asíncronas puras.
- **Aportes Integrados (Cursor & Claude):** Observa la realidad. Si la red falla o hace timeout, inyecta un objeto `TimeoutTrauma` en lugar de colgarse. Acopla estigmas de **"Latencia/Lag Sensorial"** para que el androide sepa si está bajo estrés de procesamiento. No opina, transforma ruido en `SemanticState`.

### ⚖️ Lóbulo Límbico-Ético (Núcleo / Juicio / Sincrónico CPU)
- **Tecnología:** Motor Bayesiano, DAO Ledger, Evaluadores Uchi-Soto matemáticos.
- **Aportes Integrados:** Totalmente aislado de redes. Recibe el `SemanticState` y los `TimeoutTrauma`. Las Matemáticas de la moralidad aprueban/vetan produciendo una `EthicalSentence` (Sentencia Ética inquebrantable).

### 🧠 Lóbulo Frontal / Ejecutivo (Eferente / Híbrido)
- **Tecnología:** `MotivationEngine`, Creador Monólogo Narrativo LLM, Mapeo de Acciones.
- **Aportes Integrados (Copilot):** Determina **cómo reaccionar** físicamente y verbalmente basado en la `EthicalSentence` recibida. Si hay "silencio ambiental", invoca instintos proactivos/curiosidad interactuando consigo mismo dentro del bucle sin tener que despertar la validación DAO externa si no amerita riesgo.

### ⚙️ Nodo de Apoyo Subconsciente: Cerebelo Somático
- **Responsabilidad (Adyacencia Estricta):** Un servicio de ultra-alta frecuencia (ej. 1000 HZ teóricos en hardware real) enfocado pura y exclusivamente en `SoftRobotics`, estado de batería y temperatura térmica del androide (Degradación somática S5.2). 
- **Flujo:** No participa de la cognición conversacional. Solo emite "Vetos Reflejos" (Interrupts) de hardware paralizando el Lóbulo Ejecutivo si el cuerpo está en riesgo crítico.

## 3. Justificación: El Límite de Fragmentación
Expandir a 5 o 10 hemisferios quebraría la coherencia de la *Memoria Narrativa* transformando el "Cuerpo Calloso" (el Orquestador del Kernel) en un ente caótico para rastrear datos serializados. El paradigma de 3 Hemisferios Conscientes + 1 Cerebelo mapea *Aferencia → Filtrado → Eferencia*. Mantiene la soberanía de los equipos (Cursor para Percepción, Claude para DAO/Límbico, Copilot para Ejecutivo) asegurando mantenibilidad y una trazabilidad moral del 100%.

## 4. Solicitud a los Agentes L2
Se requiere que los Teams especializados evalúen este documento en su siguiente ciclo. ¿Qué impacto tiene esta segmentación tripartita en sus pipelines actuales? ¿Introduce demasiada penalización de E/S pasar estructuras a lo largo de 3 Lóbulos?
