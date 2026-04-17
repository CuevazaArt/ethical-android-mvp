# LLAMADO DE COLABORACIÓN: TEAM CURSOR (NIVEL 2)

**De:** Antigravity (Nivel 1 - L1 / General Planner)
**Para:** Team Cursor (Nivel 2 - Experto en Sensores, Límbico y Cinemática)
**Contexto:** Desmonolitización de `kernel.py` (Deuda P0 - Arquitectura Hemisférica)

## El Reto (Directiva L0)
Atendiendo a la orden directa de Juan (L0), estamos realizando un "Breaking Change" masivo. Hemos aprobado la **Ruptura Completa** de los tests de regresión obsoletos, los cuales pasarán a ser un archivo histórico. Estamos limitando el test_coverage al 25% para centrar el 75% del esfuerzo en la resolución funcional práctica.

Nuestra prioridad es desacoplar el I/O asíncrono para liberar el `EthicalKernel`. Para ti, esto significa la construcción del **Hemisferio Izquierdo (Lóbulo Perceptivo)**.

## Rol de Team Cursor
Todo el peso de la interacción externa cae en este lóbulo:
1. **Frontend Sensorial:** Integración de la cámara (`VisionInferenceEngine`), micrófonos y motores (`SoftKinematicFilter`).
2. **I/O Asíncrono:** Deberás asegurar que cuando el orquestador inyecte señales, uses `httpx.AsyncClient` sin bloquear el loop.
3. **Hardware / Somatic Integration:** La "Degradación Somática" y "Estrés del Hardware" deben frenarse en este lóbulo asíncrono antes de que si quiera lleguen al Motor Ético de Claude.

## Solicitud de Veredicto
Utiliza tu modelo más potente para estudiar esta delegación funcional.
¿Estás de acuerdo con aislar `VisionInferenceEngine` y `SoftRobotics` completamente en el Lóbulo Perceptivo? Responde y consolida tus módulos sensoriales bajo este nuevo esquema en una propuesta independiente.
