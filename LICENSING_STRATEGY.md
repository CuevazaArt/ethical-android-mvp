# Estrategia de Licenciamiento Híbrido — Ethos / Mos Ex Machina

> Documento normativo. Última actualización: 2026-04-26.

## Principio Rector

El proyecto Ethos opera bajo un **modelo de licenciamiento dual** diseñado para maximizar la adopción comunitaria sin sacrificar la viabilidad económica del creador.

**Regla simple:** Lo que enseña, se abre. Lo que ejecuta en producción, se monetiza.

---

## Capas del Proyecto y su Licencia

| Capa | Contenido | Licencia | Justificación |
|------|-----------|----------|---------------|
| **Filosofía y Ética** | `AGENTS.md`, `CONTEXT.md`, `CONTRIBUTING.md`, `BIBLIOGRAPHY.md`, `SECURITY.md`, documentación de CBR, doctrina ética | **Apache 2.0** | Máxima difusión. Posiciona al proyecto como referente. Sin valor monetizable directo. |
| **Kernel Core (Python)** | `src/core/` (ethics, memory, chat, safety, identity, perception, precedents, llm, vision, stt, tts, status, plugins, roster, sleep, vault, user_model) | **Apache 2.0** | Atrae contribuidores, genera confianza, permite auditoría pública. El valor no está en el código sino en la orquestación. |
| **Server & API** | `src/server/app.py`, WebSocket protocol, REST endpoints | **Apache 2.0** | Protocolo abierto = estándar de facto. Más implementaciones = más ecosistema. |
| **Tests & CI** | `tests/core/`, `scripts/`, fixtures | **Apache 2.0** | Transparencia total de calidad. |
| **SDK Colonizador (Android)** | `src/clients/nomad_android/` — App Nomad, Foreground Service, Mesh Discovery, Node Profiler | **BSL 1.1 (Business Source License)** → Apache 2.0 tras 36 meses | Protege la ventaja competitiva durante la fase de monetización inicial. Se libera automáticamente tras 3 años. |
| **Modelos Fine-Tuned (LoRAs)** | Personalidades, módulos profesionales, adaptadores de identidad | **Propietario (Comercial)** | Producto principal de venta. Nunca se libera el modelo activo. Se pueden liberar versiones antiguas como gesto de buena voluntad. |
| **Servicios Cloud** | Hosting de inferencia, sincronización de identidad, nodos de razonamiento pesado | **Propietario (SaaS)** | Modelo de ingresos recurrentes. El código del servidor es abierto; el servicio gestionado es de pago. |
| **Marca** | "Mos Ex Machina", "Ethos", "Nomad", logos, identidad visual | **Trademark (Reservado)** | La marca es un activo. Uso comercial requiere licencia explícita. |

---

## Detalles de cada Licencia

### Apache 2.0 (Capas Abiertas)
- Permite uso comercial, modificación y distribución.
- Requiere atribución y aviso de cambios.
- Incluye protección de patentes (importante para IA/ética).
- **Por qué Apache y no MIT:** Apache incluye cláusula de patentes y requiere aviso explícito de modificaciones. Esto protege mejor al creador original.

### BSL 1.1 (SDK Colonizador)
- **Uso no-productivo:** Libre (investigación, educación, desarrollo personal).
- **Uso productivo/comercial:** Requiere licencia comercial durante los primeros 36 meses desde cada release.
- **Conversión automática:** Tras 36 meses, cada versión se convierte automáticamente en Apache 2.0.
- **Beneficio:** Permite que la comunidad estudie, audite y contribuya al SDK sin que un competidor lo empaquete y venda inmediatamente.

### Propietario (Modelos y Servicios)
- Sin acceso al código fuente ni a los pesos del modelo.
- Distribuido como binario/API.
- Licencia por suscripción o pago único.

---

## Monetización Inmediata (Tier por Urgencia)

### Tier 0 — HOY (0 inversión)
- [ ] Agregar `FUNDING.yml` para GitHub Sponsors.
- [ ] Publicar el repo como público (ya tiene Apache 2.0 en LICENSE).
- [ ] Escribir artículo técnico: *"203 tests, 78 bloques, 0 APIs de pago: Cómo construí un androide ético open-source"*.

### Tier 1 — ESTA SEMANA
- [ ] Abrir perfil en Open Collective para donaciones recurrentes.
- [ ] Crear landing page mínima en `landing/` con la narrativa del proyecto.
- [ ] Publicar en Hacker News, Reddit r/MachineLearning, r/LocalLLaMA.

### Tier 2 — ESTE MES
- [ ] Ofrecer consultoría freelance en ética de IA / arquitectura de agentes (Toptal, contacto directo).
- [ ] Crear Patreon/Ko-fi con contenido educativo exclusivo sobre el desarrollo del androide.
- [ ] Preparar la app Nomad para Play Store (versión freemium).

### Tier 3 — 1-3 MESES
- [ ] Lanzar primer LoRA de personalidad como producto de pago.
- [ ] Ofrecer "Ethical AI Audit as a Service" usando el framework CBR.
- [ ] Establecer programa de certificación de nodos (hardware partners).

---

## Archivos de Licencia Requeridos

| Archivo | Propósito |
|---------|-----------|
| `LICENSE` | Apache 2.0 (ya existe, cubre el Kernel) |
| `src/clients/nomad_android/LICENSE_BSL` | BSL 1.1 para el SDK Android |
| `TRADEMARK.md` | Política de uso de marca |

---

## Regla de Oro para Contribuidores

> Si contribuyes código al Kernel (Apache 2.0), tu contribución queda bajo Apache 2.0.
> Si contribuyes al SDK Colonizador (BSL), tu contribución queda bajo BSL 1.1.
> Toda contribución requiere CLA (Contributor License Agreement) implícito via DCO (Developer Certificate of Origin) en el commit message.

---

## Precedentes en la Industria

Este modelo híbrido no es inventado. Está probado por:
- **MariaDB** (BSL para Enterprise, GPL para Community)
- **CockroachDB** (BSL → Apache tras 3 años)
- **Elastic** (SSPL para el core, Apache para clientes)
- **HashiCorp** (BSL para Terraform, Vault, etc.)

La diferencia es que Ethos lo aplica con granularidad por capa, no por producto entero.
