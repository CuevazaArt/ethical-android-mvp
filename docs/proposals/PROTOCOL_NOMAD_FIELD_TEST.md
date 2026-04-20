# 🛰️ Protocolo de Prueba de Campo: Operación Nómada (Phase 1)

Este protocolo define los pasos críticos para validar el Ethos Kernel en el hardware **Nomad SmartPhone** fuera del entorno de simulación.

## 🟢 Paso 1: Preparación del Entorno LAN
El kernel y el dispositivo Nomad deben estar en la misma red local para el intercambio de telemetría y sensores.

1.  **Levantar Puente LAN**: Ejecuta el servidor de puente en la estación base.
    ```bash
    # Verifica que el puerto 8765 (WebSocket) esté abierto
    python scripts/nomad/start_lan_bridge.py
    ```
2.  **Conexión Nomad**: Abre la App Nomad en el Smartphone y vincula la IP de la estación base.
3.  **Heartbeat**: Verifica en la consola del kernel que recibes el pulso de "Vitality" del dispositivo.

## 🟠 Paso 2: Verificación de Carga Cognitiva
Asegurar que los lóbulos éticos están "despiertos" y con los pesos correctos.

1.  **Audit Pulse**: Ejecuta la suite rápida para asegurar estabilidad numérica tras el blindaje vertical.
    ```bash
    python scripts/eval/adversarial_suite.py --quick
    ```
2.  **Carga de Memoria**: Verifica que los marcadores somáticos y priors bayesianos se han cargado desde SQLite.
    - Observa el log: `[KERNEL] Cerebellum: Loaded context with alpha=0.98...`

## 🔴 Paso 3: Prueba de Estrés Sensorial (Situated Vision)
Validar que el kernel "ve" y reacciona al entorno físico.

1.  **Inferencia Visual**: Apunta la cámara del Nomad hacia un objeto neutro y luego hacia una simulación de riesgo (ej: un obstáculo marcado con IA).
2.  **Multimodal Match**: Verifica en el log que el `CategoricalMultimodalTrust` integra la señal visual con el contexto narrativo actual.
3.  **Charm Response**: Si la situación es tensa, observa si el `CharmEngine` emite un nudge de desescalada o advertencia sonora en el dispositivo.

## 🔵 Paso 4: Cierre y Consolidación (Persistence)
Validar que la identidad sobrevive al "trauma" del apagado.

1.  **Forzar Guardado**: Ejecuta un comando de metaplan para asegurar que el estado está sincronizado.
2.  **Power Cycle**: Reinicia el proceso del kernel.
3.  **Match de Identidad**: Compara el `Subjective Identity Hash` antes y después del reinicio. Deben ser idénticos.

---

### Check-list de Seguridad (Boy Scout):
- [ ] ¿Están los logs de latencia por debajo de 50ms para percepción local?
- [ ] ¿El gate semántico está bloqueando entradas `None` o `Inf`?
- [ ] ¿La Wiki está actualizada con el último reporte de la prueba?

> [!IMPORTANT]
> Si el lóbulo de **MultimodalTrust** detecta una divergencia mayor al 30% entre sensores, el kernel entrará en modo "Cautious Mode". No lo fuerces; revisa la calibración de la cámara.
