# PROPOSAL: Arquitectura Conversacional Seductora V2 (Modelo Consolidado)

**Fecha:** 2026-04-17
**Autor:** Antigravity L1 (Síntesis de Aportación Final L3-Exterior)
**Estado:** Documento Fundacional Definitivo para Módulo V2

## 1. Visión General
Esta propuesta cierra el ciclo de diseño conceptual para el **Motor de Encanto y Gestión de Turnos**. Representa la síntesis definitiva entre las aportaciones teóricas (Sociolingüística, HRI) y la cruda realidad del hardware Edge. Corrige el sobre-idealismo de los modelos LLM-puros integrando una arquitectura somática e híbrida.

## 2. Los Ejes de Solución (Mapeo a la Arquitectura Tri-Lobulada)

### A. Robustez Sensorial (El Lóbulo Perceptivo)
*   **Problema:** Depender sólo de micrófonos (VAD acústico) en el mundo real es inútil por el ruido ambiental.
*   **Solución (VVAD):** Se implementa *Visual Voice Activity Detection*. El Androide usa la cámara para leer el movimiento labial de la persona o el tracking de su rostro al hablar, fusionándolo con el audio. Si el audio falla o colapsa por ruido, la vista (VVAD) manda. 
*   **Fallback:** Si ambos sensores degradan por mala luz o ruido extremo, el Androide suspende el Motor de Encanto (dejando de tomar turnos riesgosos) y entra en "Modo de Supervivencia Social" utilizando un LLM miniatura solo para asentar presencia inofensiva.

### B. Amortiguación Emocional (Ganglios Basales)
*   **Problema:** Transitar parámetros variables de 0 a 1 de golpe crea a un monstruo sociópata.
*   **Solución:** Los *Ganglios Basales* (subrutina en el Ejecutivo) obligan a que todo cambio de estilo pase por un filtro temporal de suavizado (Exponential Moving Average / Filtros de Kalman). Retraer intimidad (Tatemae) o revelar empatía (Honne) ocurre en curvas de segundos, nunca en milisegundos.

### C. El Tribunal Ético de Dos Niveles (Doble Loop)
En lugar de embotellar el pipeline bloqueando la voz esperando a la nube, la Ética se divide en dos:
1.  **Corte Marcial Local (Nivel 1 - 50ms):** El *CerebellumNode* / Edge Board tiene Reglas Deontológicas estrictamente codificadas e inmutables. Si un humano pide al Androide que lastime a alguien, este Tribunal interrumpe y bloquea de manera instintiva sin consultar internet.
2.  **Suprema Corte Nube (Nivel 2 - Posterior):** Mientras el robot habla, el *Lóbulo Límbico* en la nube contextualiza, pondera y clasifica el riesgo socioemocional a medio plazo. Puede ordenar un ajuste de políticas (bajando la calidez o aplicando reprimendas) en los turnos *subsecuentes*, no de forma bloqueante-instantánea.

## 3. Hoja de Ruta Inmediata
Con la teoría finalizada, las prioridades de ingeniería (Ejecución L2) se desplazan a:
1.  **Prototipar Pipeline VVAD:** Instalar los flujos de lectura labial / VAD en el Daemon de Visión.
2.  **Tribunal Ético Local:** Desacoplar las `AbsoluteEvil` rules del Kernel P0 y cablearlas directamente en el ciclo de 100Hz del Edge. 
3.  **Simulaciones ABM Básicas:** Crear perfiles mock de "Usuario Agresivo", "Usuario Pasivo" para ensayar las respuestas temporales (Smoothing de Calidez) sin hardware físico aún.

Este documento consolida la arquitectura social. El conocimiento teórico está sellado.
