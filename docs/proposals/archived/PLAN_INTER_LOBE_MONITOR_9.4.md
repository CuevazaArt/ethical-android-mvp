# Plan de Implementación: Monitor de Stream Inter-Lóbulos (Tarea 9.4)

## Objetivo
Cumplir la Tarea 9.4 del **Bloque 9 (Nomadismo Perceptivo)** para el equipo VisualStudio (actualmente exhaustos). Se implementará un monitor que permita al kernel reaccionar proactivamente a estímulos sensoriales continuos (E-Stop / Alerta) sin esperar a que el usuario escriba.

## 🛠️ Componentes a Desarrollar/Modificar

### 1. `src/kernel_lobes/perception_lobe.py`
- Añadir un callback opcional `urgent_notification_callback` al `PerceptiveLobe`.
- En `absorb_episode`, si un episodio tiene `is_urgent > 0.8`, disparar el callback.

### 2. `src/kernel.py`
- Añadir `self.proactive_sensory_event = asyncio.Event()` en `EthicalKernel`.
- Suscribir al kernel como listener de alertas urgentes del `PerceptiveLobe`.
- Implementar `handle_proactive_sensory_alert()` que prepara el estado del kernel para una interrupción (E-Stop).

### 3. `src/chat_server.py` (Opcional pero recomendado para realismo)
- El bucle principal de WebSocket debe "esperar" tanto mensajes del usuario como el `proactive_sensory_event`.

### 4. `tests/test_inter_lobe_stream.py` (Test de Validación 9.4)
- Mockear el `VisionContinuousDaemon`.
- Inyectar una ráfaga de episodios normales.
- Inyectar un episodio crítico ("Hostile entity detected").
- Validar que el evento proactivo se dispara y el kernel transiciona a estado de alerta.

## 📅 Cronograma (Instántaneo)
1. **Paso 1**: Modificar `PerceptiveLobe` para notificaciones.
2. **Paso 2**: Modificar `EthicalKernel` para gestionar el evento.
3. **Paso 3**: Crear el test de integración inter-lobular.

> [!NOTE]
> Esto cierra el vacío de proactividad en el ciclo Tri-lobulado, permitiendo que el androide "despierte" ante el peligro.
