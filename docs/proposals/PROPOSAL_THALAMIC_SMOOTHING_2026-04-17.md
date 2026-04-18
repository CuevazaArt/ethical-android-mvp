# PROPOSAL: Suavizado Motor y Filtrado (Lóbulo Talámico / Ganglios Basales)

**Fecha:** 2026-04-17
**Autor:** Antigravity L1 & Juan L0
**Estado:** Propuesta Conceptual a futuro (Mitigación de Latencia y Valle Inquietante)

## 1. El Problema: Imperfección Sensorial y Cambios Abruptos
Durante el diseño del **Motor de Encanto (Módulo 10)** y el **Sistema de Turnos Multimodales**, identificamos dos vulnerabilidades físicas severas en la robótica de consumo actual (incluyendo Raspberry/Smartphones):
1.  **VAD Sucio:** Los micrófonos recogen ruidos ambientales, forzando al sistema de turnos a reaccionar, interrumpiendo el flujo.
2.  **Transiciones Sociopáticas:** Parametrizar la "Calidez" o el "Misterio" significa que un falso positivo de hostilidad puede causar que el androide pase de ser íntimamente cálido a gélido (Tatemae) en cuestión de 1 milisegundo, arruinando la ilusión de empatía.

## 2. Solución Biológica: Nueva Capa Arquitectónica
Se asume que la latencia de inferencia tenderá a cero en el futuro gracias a NPUs integradas y redes 6G. Sin embargo, el *smoothing* conductual debe estar codificado en la arquitectura base. Proponemos la adición de dos estructuras sub-cognitivas:

### A. Lóbulo Talámico (El Enrutador de Sentidos)
*   **Función:** Relevo y filtrado sensorial en el Edge.
*   **Operación:** Antes de que una señal sónica despierte al **PerceptiveLobe**, el procesador local ejecuta una validación binaria ultraligera para diferenciar Voz Humana Dirigida vs. Ruido Ambiental. Protege al sistema cognitivo de "alucinaciones de interrupción".

### B. Ganglios Basales (El Amortiguador Emocional)
*   **Función:** Rampa de inercia para los vectores del *Motor de Encanto*.
*   **Operación:** Si el **Lóbulo Ejecutivo** instruye bajar la Calidez de `0.8` a `0.2`, los Ganglios Basales interceptan la orden y aplican un "promedio móvil". En el turno 1 baja a `0.6`, en el turno 2 a `0.4`, etc. Esto asegura transiciones emocionales orgánicas y elimina el comportamiento robótico/sociópata en las interacciones íntimas.

## 3. Conclusión
Esta adición sella las fisuras entre el plano cognitivo masivo (LLMs) y la realidad física y ruidosa del hardware periférico. Quedará en cola para la implementación del **Módulo V2 Kinect/Sensor**.
