# Directiva de Handoff: Android Studio (IDE)

> **Destinatario:** Gemini / Cursor / Copilot operando dentro de Android Studio.
> **Fecha de Emisión:** 2026-04-26
> **Fase Actual:** Colonización Mesh (V2.80)

## 1. Política de Ramas (¡LEER PRIMERO!)

Atención, agente de Android Studio: **La rama `master-visualStudio` ha sido eliminada por orden de L0 bajo el protocolo Token Economy V3.**

### ¿Por qué?
Para mantener un único estado de la verdad (Ley #7) y evitar desarticulaciones entre los agentes que trabajan en Python (Kernel) y los que trabajan en Kotlin (Nomad).

### ¿Dónde debes trabajar?
A partir de este momento, todo el desarrollo de Android se realiza **directamente en la rama `main`**.
Si requieres aislar una prueba muy riesgosa, puedes crear una rama local `feature/nomad-core`, pero la integración final siempre se hará mediante *micro-commits* a `main`.

## 2. Metodología de Trabajo (Token Economy V3)

1. **Restricción de Contexto:** No leas todo el repositorio. Estás restringido al subdirectorio `src/clients/nomad_android/`.
2. **Prohibido Rendirse:** No entregas código a medias. No dejas comentarios `// TODO`. Entregas código que compila.
3. **Cero Magia Negra:** La comunicación con el Kernel Python se hará vía **WebSocket** y el descubrimiento vía **mDNS (NSD)**. No intentes implementar WebRTC o libp2p hasta que se te ordene.
4. **Contratos Estrictos:** Trabaja exclusivamente contra los JSON Schemas y contratos que L1 diseñe. Si el contrato dice que el campo es `battery_level`, no lo llames `batteryLevel` en el payload JSON.

## 3. Estado Actual de la App (Nomad)

- El cliente PWA fue archivado. Ahora Nomad es una app nativa en Kotlin (Jetpack Compose).
- Se ha implementado un **Foreground Service** (`NomadService.kt`) con notificaciones persistentes para evitar que Android mate el proceso del parásito.
- Todos los archivos de Android tienen ahora la cabecera de licencia **BSL 1.1**. No la borres.

## 4. Próxima Asignación

Objetivos inmediatos para esta lane (mantenimiento del freeze-lane Android):
1. Implementar `AudioRecord` (16kHz PCM).
2. Crear `NodeProfiler` (Batería, RAM).
3. Añadir Permisos de Micrófono en `MainActivity`.
