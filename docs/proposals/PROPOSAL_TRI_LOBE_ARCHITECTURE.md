# PROPOSAL: Arquitectura Tri-Lobulada (Triune Brain)

**Autor:** Antigravity (Nivel 1 / General Planner) & L0 (Juan)
**Estado:** `PROPUESED` PARA DELIBERACIÓN
**Fecha:** Abril 2026

## 1. Motivación (El Problema con 2 Hemisferios)
La arquitectura previa proponía dividir `kernel.py` en 2 hemisferios: **Perceptivo (Asíncrono E/S)** y **Ético (Sincrónico CPU)**. Aunque resolvía los bloqueos de E/S de red, dejaba un problema oculto: el Hemisferio Ético, además de juzgar la moralidad (matemáticas booleanas de la DAO), también tenía que ocuparse secundariamente de invocar LLMs para estructurar las respuestas ejecutivas y redactar el *Narrative Arc*. 
Moralidad y Ejecución de Acciones son responsabilidades cognitivas distintas.

## 2. Propuesta: El Modelo de 3 Lóbulos
Se propone fragmentar el Kernel en tres dominios aislados interconectados por un Orquestador ligero (Cuerpo Calloso):

### 👁️ Lóbulo Perceptivo (Aferente / Sensorial)
- **Tecnología Principal:** `httpx.AsyncClient`, visores multimodales, colas asíncronas puras.
- **Responsabilidad:** Observar la realidad, recibir payloads JSON del exterior, ejecutar STT (Speech-to-Text) o parsing visual.
- **Salida:** Genera un `SemanticState` estandarizado. No opina, solo transforma ruido en metadatos y estampa "Tiempos de Latencia (Hardware lag y stress)".

### ⚖️ Lóbulo Límbico-Ético (Núcleo / Juicio)
- **Tecnología Principal:** Carga sincrónica CPU-bound, Matemáticas, Evaluadores bayesianos.
- **Responsabilidad:** Funcionar como un *semáforo*. Recibe el `SemanticState` y lo hace pasar por los Guardianes Rígidos (AbsoluteEvil, DAO, Uchi-Soto). 
- **Salida:** Genera un `EthicalSentence` (Sentencia Ética que indica tensión social y umbrales de aprobación/veto). No es responsable de generar texto, solo aprueba/deniega matemáticamente la intención detectada.

### 🧠 Lóbulo Ejecutivo (Eferente / Motor)
- **Tecnología Principal:** `MotivationEngine`, LLMs degenerativos para redacción de monólogo y planes.
- **Responsabilidad:** Determinar **cómo reaccionar**. Recibe los metadatos visuales y la `EthicalSentence`.
- **Acción:** Si el mandato ético es "Seguro", redacta la respuesta amigable; si "Hay Tensión de 0.8", se fuerza un Output cauteloso y asustadizo; si "Veto Total", dispara respuestas secas de Fallback. Adicionalmente, durante su tiempo libre, enciende la Curiosidad Proactiva en el fondo.

## 3. Beneficios Esperados
1. **Separación de Concernes Radical:** Permite que las Reglas Morales (Lóbulo Ético) sean inmutables, estables y testeables unitariamente al 100% sin necesidad de simular un LLM redactando.
2. **Claridad Operacional para Equipos:**
    - Team Cursor se hace dueño absoluto del Lóbulo Perceptivo.
    - Team Claude gobierna el Límbico-Ético (DAO, Recompensas).
    - Team Copilot e instancias adicionales se dedican a la redacción y planeamiento del Frontal/Ejecutivo (Eficiencia Python).

## 4. Solicitud a los Agentes L2
Se requiere que los Teams especializados evalúen este documento en su siguiente ciclo. ¿Qué impacto tiene esta segmentación tripartita en sus pipelines actuales? ¿Introduce demasiada penalización de E/S pasar estructuras a lo largo de 3 Lóbulos?
