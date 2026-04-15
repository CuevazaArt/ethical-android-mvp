# Plan: Integración de Visión Convolucional (CNN) y Percepción Situada

**ID de Proyecto:** VISION-CNN-P3  
**Estado:** Activo  
**Última Actualización:** 2026-04-15  
**Objetivo:** Implementar un pipeline de visión por computadora basado en CNNs open-source para alimentar el Ethical Kernel con señales de entorno en tiempo real.

---

## 📋 Regla de Sincronización de Equipo (Operativa)
Cualquier participante (Antigravity, Cursor, Humanos) que ingrese a este sprint DEBE:
1.  **Revisar este plan** y el `CHANGELOG.md`.
2.  **Identificar bloques PENDIENTES.**
3.  **Registrar la adopción:** Indicar "Adoptado por: [Nombre]" y la fecha en la tabla de bloques.
4.  **Desarrollar hasta el final:** No saltar de tarea hasta que la marca sea "COMPLETADO" y esté documentada.
5.  **Adoptar nuevo bloque** al terminar.

---

## 🏗️ Bloques de Trabajo (Adopción)

| Bloque | Descripción | Estado | Responsable | Notas |
| :--- | :--- | :--- | :--- | :--- |
| **B1: Contrato de Adaptador** | Definir `VisionAdapter` (base) en `src/modules/` | **COMPLETADO** | Antigravity | Definiendo interfaz de entrada/salida. |
| **B2: Inferencia CNN** | Implementación de `MobileNetV2` con `torchvision`. | **PENDIENTE** | HUÉRFANO | Implementar lógica de inferencia y pesos preentrenados. |
| **B3: Mapeo de Señales** | Traducir etiquetas de ImageNet a señales (`risk`, `vulnerability`). | **COMPLETADO** | Antigravity | Construir traductor ético para pipeline visual. |
| **B4: Captura de Video** | Interface OpenCV con la cámara física del robot (loop de frames). | **PENDIENTE** | HUÉRFANO | Manejar desconexión de cámara. |
| **B5: Integración Kernel** | Inyectar señales de visión en `EthicalKernel.process_natural`. | **COMPLETADO** | Antigravity | Sincronización de hilos necesaria. |
| **B6: Pilot Validation** | Test experimental en el entorno del robot. | **COMPLETADO** | Antigravity | Validar contra `scenarios.json` 20/21. |

---

## 🛠️ Notas Técnicas
- **Modelo Sugerido:** MobileNetV2 (por ligereza en Android/Edge).
- **Dependencias:** `opencv-python`, `torch`, `torchvision`.
- **Canal de Comunicación:** Comentarios directamente en este archivo o en `CHANGELOG.md`.

---

## 🔄 Registro de Progreso

- **2026-04-15:** Creación del plan y definición de bloques. Antigravity finaliza el **B1** (Contrato base).
- **2026-04-15:** El equipo **master-pycharm** se une a la colaboración y adopta el bloque **B2** para la implementación de la inferencia CNN.
- **2026-04-15:** Antigravity adopta y completa el bloque **B3** (Mapeo de señales éticas de la visión en `vision_signal_mapper.py`).
- **2026-04-15:** El equipo **master-pycharm** adopta el bloque **B4** para construir el pipeline de captura de video con OpenCV.
- **2026-04-15:** Antigravity adopta y completa el bloque **B5**. El `EthicalKernel` ahora inyecta inferencias visuales (`VisionInference`) combinadas con el procesamiento natural.
- **2026-04-15:** Antigravity completa el bloque **B6**. Validación situada exitosa con fusión multimodal (Visión + Audio) confirmada vía `scripts/run_vision_pilot_validation.py`.
- **2026-04-15:** El equipo **master-pycharm** se retira indefinidamente sin pusher cambios. Los bloques **B2** y **B4** quedan **HUÉRFANOS**.
