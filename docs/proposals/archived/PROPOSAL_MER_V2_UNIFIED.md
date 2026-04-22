# Proyecto de Modelo Unificado: Motor de Encanto Resiliente (MER V2)

**Documento Maestro de Arquitectura y Distribución**
**Versión:** 2.0 Final Consolidada
**Fecha:** 2026-04-17

Este documento recopila de forma definitiva todos los aportes sociolingüísticos, cognitivos y de ingeniería de Hardware/Edge debatidos para el establecimiento del **Motor de Encanto Resiliente**. Sustituye a los borradores fragmentados.

## 1. El Postulado MER (Motor de Encanto Resiliente)
Un Motor de Encanto sostenible debe ser gradual en la expresión afectiva, redundante en la percepción física y centralizado-distribuido en la toma ética.

El modelo se sostiene sobre tres pilares fundamentales:
1. **Continuidad Afectiva (Anti-Sociopatía):** La empatía y el misterio se desplazan fluidamente en el tiempo (Smoothing).
2. **Robustez Sensorial (Anti-Alucinación):** Los fallos del micrófono y falsos audios no pueden detener la cognición.
3. **Ética de Doble Nivel (Anti-Latencia):** La censura instantánea ocurre en C++/Edge local, la validación sociológica ocurre asíncronamente.

---

## 2. Componentes Clave de la Arquitectura

### A. Percepción Resiliente (Thalamic Node)
El androide cuenta con un Lóbulo Talámico operando en el Edge (*CerebellumNode* pipeline).
*   **Fusión VVAD + VAD:** Unifica el detector de voz con el movimiento labial (OpenCV/Edge AI) para ignorar ruidos ambientales como tráfico o música.
*   **Modo Presencia (Degradación Grácil):** Si la calidad de la señal cae, el sistema adopta un comportamiento neutro ("Modo de Presencia") respondiendo con gestos leves en lugar de intentar forzar turnos complejos.

### B. Smoothing Afectivo (Ganglios Basales)
Transformación del modelo matemático de Tatemae/Honne.
*   **Filtros Kalman/EMA:** Integrados dentro de `UserModelTracker` para las variables de `warmth`, `mystery`, e `intimacy`.
*   **Transiciones Graduales:** Los cambios conductuales demoran al menos 5 segundos en aplicarse completamente bajo umbrales de inercia, imitando las reacciones hormonales biológicas.

### C. Orquestador Predictivo (Turn Manager)
Emulando dinámica de grupos N:N (múltiples humanos).
*   **Agent-Based-Modeling (ABM) Local:** Lazo cerrado que predice el impacto de interrumpir la conversación. Evita que el Androide monopolice la escena.
*   **Prefetch con Micro-LLM:** Un modelo local (Edge) predice frases puente ("Mmm", "Es decir...") mientras la Nube formula la respuesta creativa sustancial, rompiendo la barrera perceptual de la espera.

### D. Tribunal Ético Distribuido (El Escudo Local)
Por carencia temporal de redes 6G/7G, el Tribunal DAO se desacopla temporalmente de la validación Turn-by-Turn para evitar bloqueos.
1.  **Nivel 1 (Deontológico de Fuego Rápido - 50ms):** Filtros inamovibles corriendo en Python Edge puro. Bloquean apología al daño y doxxing antes de que llegue a comprensión profunda.
2.  **Nivel 2 (Conciencia y Riesgo Límbico):** Modelo local-asíncrono que evalúa Uchi/Soto, el riesgo de manipulación y ajusta el Smoothing en retrospectiva sin interrumpir la dicción actual.

### E. Memoria Jerárquica
`NarrativeMemory` se fragmenta en:
1.  **Inmediata:** Embbedings de la sesión actual de Chat y eventos vitales (IPU).
2.  **Episódica:** Promesas y revelaciones críticas.
3.  **Identidad:** Preferencias consolidadas y firmas de confianza de usuario.

---

## 3. Plan de Implementación Distribuido (L2 Squads)

La refactorización descrita se delega a la Escuadra de Capa 2 (L2) siguiendo el `PLAN_WORK_DISTRIBUTION_TREE.md`:

| Escuadrón / Team | Responsabilidad Asignada | Target (Bloque MER) |
| :--- | :--- | :--- |
| **Team Cursor** | Operaciones Sensoriales | Desarrollar `ThalamusNode` y fusionar VVAD + VAD. Operando como Daemon asíncrono para no bloquear `main`. |
| **Team Antigravity** | Regulador Límbico y DAO | Partir el Tribunal de Ética. Mover `AbsoluteEvil` Detector a la rampa de 50ms (Nivel 1 Edge). |
| **Team Claude** | Inercia Conductual (Smoothing) | Modelar `BasalGanglia` sobre `UserModelTracker` para aplicar filtros matemáticos a `warmth`/`mystery` (Evitar "Sociopatía paramétrica"). |
| **Team Copilot** | Prefetching y Heurísticas | Inyectar estúpidos algorítmicos probabilísticos de Frases Puente locales, antes de cargar un Micro-LLM puro por cuestiones de dependencia. |

Este documento sella la Arquitectura 2.0. Las ramas L2 deben asimilar esta directiva, unificarse hacia `main` (Resolviendo conflictos localmente bajo el paradigma OGA) e iniciar su desarrollo asignado.
