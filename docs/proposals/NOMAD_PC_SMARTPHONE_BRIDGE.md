# Primer puente nomada: PC ↔ smartphone y capas por clase de hardware

Este documento fija el **marco** para la capacidad nómada entre **PC (cerebro / cómputo)** y **smartphone (cuerpo ligero / sensores)**, sin confundir el MVP actual con el despliegue final. Complementa [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md), [PROPUESTA_CONCIENCIA_NOMADA_HAL.md](PROPUESTA_CONCIENCIA_NOMADA_HAL.md) y [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

---

## 1. Qué es el “primer puente”

Hoy el repositorio ofrece:

- **Transporte:** WebSocket + HTTP en LAN (`CHAT_HOST`, `mobile.html`, checkpoints y conduct guide al cerrar sesión).
- **Ética:** el mismo `EthicalKernel` en el servidor; el móvil **no** sustituye el núcleo normativo.

Ese conjunto es el **primer puente operativo** hacia la **capacidad nómada PC–smartphone**: mismo protocolo de diálogo, continuidad opcional en disco en el PC, y base para añadir **cuerpo sensorial** y **saltos de runtime** sin redefinir MalAbs.

Cada **clase de hardware** (PC de escritorio, portátil, smartphone Android/iOS, wearables futuros, edge dedicado) tendrá **su desarrollo específico** y **sus capas de compatibilidad** a construir: no existe un único binario universal; existe un **contrato común** (mensajes, snapshot, HAL) y **adaptadores por plataforma**.

---

## 2. Clases de hardware y capas de compatibilidad (a desarrollar)

| Clase | Rol típico | Capas de compatibilidad (ejemplos, no exhaustivo) |
|-------|------------|---------------------------------------------------|
| **PC / workstation** | Kernel completo, LLM pesado, checkpoints en disco | Python 3.9+, dependencias `requirements.txt`, opcional Ollama; firewall OS. |
| **Smartphone (browser)** | Cliente ligero + **primer acceso a sensores vía web** (cuando el navegador exponga APIs) | Misma página `mobile.html` / extensión futura; objeto `sensor` en JSON del WebSocket ([README](README.md), v8). |
| **Smartphone (app nativa futura)** | Sensores de bajo nivel, mejor latencia, offline parcial | Contrato de empaquetado (WebSocket/TLS), permisos OS, posible bridge nativo → JSON `sensor`. |
| **Otro edge** | Sólo inferencia pequeña o relé | [conduct_guide_export](../src/modules/conduct_guide_export.py), destilación ([context_distillation](../src/modules/context_distillation.py)), schema de snapshot. |

**Principio:** la **lógica ética** permanece en los caminos documentados del kernel; las **capas de compatibilidad** son transporte, permisos, formato de sensores, seguridad de red y empaquetado — cada una evoluciona por clase de dispositivo.

---

## 3. Oportunidad inmediata: percepción sensorial diversa y coordinada (smartphone)

El hardware del **smartphone** es la **oportunidad inmediata** para las **primeras aproximaciones** a una **percepción sensorial diversa y coordinada**:

- El protocolo ya admite un objeto **`sensor`** en el cliente (situación v8: batería, ruido, señales de emergencia multimodal, etc.).
- Desde el móvil, en modo **thin client**, esos valores pueden **inyectarse en el mensaje** (cuando la UI o una capa intermedia los rellene) y el kernel los fusiona en **señales simpáticas** sin bypass de MalAbs.

**Estado actual:** `mobile.html` envía texto; la **siguiente iteración de producto** en este puente es enriquecer el cliente móvil para **mapear** lecturas disponibles (API web, o entrada manual de prueba) al esquema `sensor`, y documentar límites por navegador.

---

## 4. Alcance de red y testeo de campo

- **Hoy:** despliegue pensado para **LAN doméstica de confianza** (sin TLS en el tramo local; ver [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)).
- **Testeo de campo en una red más segura** (VPN, túnel, TLS terminado en proxy, red segmentada, etc.) queda **pendiente de criterio del operador** — se activará **cuando se indique**, para no mezclar en el mismo hito la validación ética del kernel con el endurecimiento de infraestructura.

Hasta entonces, la documentación trata el entorno LAN como **laboratorio controlado**, no como producción expuesta a Internet abierta.

---

## 5. Referencias cruzadas

| Documento | Contenido relacionado |
|-----------|------------------------|
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | Pasos concretos PC + móvil, firewall, `mobile.html` |
| [PROPUESTA_CONCIENCIA_NOMADA_HAL.md](PROPUESTA_CONCIENCIA_NOMADA_HAL.md) | HAL, runtime dual, transmutación |
| [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) | Contrato sensorial y capas situadas |
| [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) | Ruta P0–P3 y riesgos operativos |

---

*Ex Machina Foundation — puente nomada PC–smartphone; alinear con CHANGELOG e HISTORY.*
