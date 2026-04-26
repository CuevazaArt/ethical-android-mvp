# Nomad PWA Archive (V2.76)

Este directorio contiene el código congelado del cliente web PWA original (Nomad).
Se ha tomado la decisión arquitectónica de **abandonar el enfoque PWA** y migrar a un **SDK Android Nativo** por las siguientes razones críticas descubiertas durante el desarrollo de la Fase 22:

## Limitaciones Críticas (Muro de Cristal de la PWA)
1. **Pausa en Segundo Plano (Background Death):** Cuando el navegador móvil se minimiza o la pantalla se bloquea, el hilo JS y el WebSocket mueren, rompiendo la continuidad sensorial e impidiendo que Ethos funcione como un agente activo o "ángel de la guarda" en el bolsillo.
2. **Acceso Sensorial Limitado:** Imposibilidad de leer métricas del sistema profundas sin intervención o permisos frágiles (batería, hardware crudo).
3. **Flujo de Audio Ineficiente:** El AEC (Cancelación de Eco Acústico) del navegador bloquea a veces el feed del micrófono, y la conversión del formato WebM a PCM consume recursos en el backend.

## Reorientación a Android Nativo
El proyecto ahora apunta a un cliente **Android en Kotlin** utilizando:
- **Foreground Service:** Para mantener la conexión WebSocket abierta y activa 24/7 incluso con la pantalla apagada.
- **AudioRecord:** Para capturar audio PCM puro.
- **CameraX:** Para visión estelar.
- **On-Device Wake Words:** (e.g. Porcupine) para despabilar a Ethos sin transmitir streaming 100% al backend.

*Este código queda archivado como referencia visual (UI) y de flujo.*
