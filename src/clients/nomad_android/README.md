# Nomad Android SDK (Fase 23)

Este directorio contendrá la aplicación nativa en Android/Kotlin para el agente Ethos (Nómada).
La principal motivación de esta arquitectura es proveer un cliente "Always-On" capaz de:
- Correr en un `ForegroundService` con un WebSocket persistente en background.
- Capturar `AudioRecord` (PCM puro) para un canal continuo sin AEC agresivo del navegador.
- Capturar `CameraX` a voluntad del modelo.
- Proveer biometría y telemetría de hardware (Luz, Batería, Acelerómetro) continuamente.

**Próximos Pasos (Arquitectura):**
1. Configurar Gradle / Jetpack Compose.
2. Implementar Cliente OkHttp WebSocket.
3. Crear `SensoryService` (Foreground Service).
