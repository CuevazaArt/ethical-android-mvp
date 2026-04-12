# Estrategia, ruta y riesgos — Ethos Kernel

Documento de **síntesis** (abril 2026): conclusiones de revisión del proyecto, expectativas realistas, **readaptación de la ruta**, y el **hueco principal** que prioriza el trabajo siguiente.

**Relación con otros docs:** el núcleo normativo y las capas advisory siguen descritos en [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) y [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). Las PROPUESTA en `docs/proposals/` son diseño; este archivo es **gobierno de producto / operación**.

**Índice rápido (coherencia 2026):** [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) · [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) · [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) · [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) · [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) · [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) · [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) · [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) · [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) · [adr/README.md](adr/README.md).

---

## 1. Dónde estamos (hecho verificable)

- El repositorio es un **MVP de runtime** sobre un kernel ético (v5) con **simulaciones fijas**, **chat WebSocket**, persistencia versionada, **mocks de gobernanza** (DAO, tribunal simulado), hub constitucional, **HAL / identidad nómada**, auditoría tipo `HubAudit`, y **cifrado opcional** de checkpoints JSON.
- La **suite de tests** cubre invariantes del núcleo y pruebas de humo/integración del servidor; CI instala `requirements.txt` y ejecuta `pytest` en Python 3.11 y 3.12.
- La **documentación** (CHANGELOG, HISTORY, PROPUESTA) es rica; el riesgo no es falta de texto sino **coherencia operativa** entre combinaciones de `KERNEL_*`.

---

## 2. Conclusiones registradas (crítica constructiva)

### 2.1 Fortalezas

- **Invariantes éticos** con tests dedicados; el runtime no sustituye el núcleo sino que lo envuelve con flags.
- **Persistencia versionada** y migración desde snapshots antiguos favorecen continuidad de demos y desarrollo.
- **Mocks explícitos** (DAO, corte, vault) evitan confundir demo con infraestructura distribuida real.
- **Trazas y auditoría** (`HubAudit`, líneas en DAO) ayudan a narrativa y depuración; no son por sí solas evidencia legal o criptográfica.

### 2.2 Expectativas vs. lo que el código puede prometer

| Ámbito | Expectativa frecuente | Realidad del MVP |
|--------|------------------------|------------------|
| Gobernanza | “Democracia real” | Pipeline **off-chain** en proceso + estado en snapshot; sin red, identidad fuerte ni modelo de amenazas distribuido. |
| Seguridad / privacidad | “Datos protegidos” | Fernet en **JSON en disco**; SQLite sigue en texto plano; el modelo de amenaza debe documentarse por capa. |
| Conciencia nómada | “Continuidad hardware” | Abstracción HAL + narrativa + auditoría; integridad física real sigue **declarativa / stub** donde no haya integración. |
| Coherencia de producto | “Un solo producto” | Muchas dimensiones (ética, relacional, sensores, judicial, hub, nómada); la coherencia pasa por **contratos** y **perfiles** soportados. |

### 2.3 Riesgos activos

1. **Complejidad operativa:** combinatoria de variables de entorno; sin perfiles nominales, el mantenimiento y el soporte se vuelven caros.
2. **Dos mundos:** pipeline ético formal vs. capas advisory; las capas deben seguir documentadas como **no veto** salvo que el contrato diga lo contrario.
3. **Documentación vs. velocidad:** más PROPUESTA no sustituye un **índice de estado** (qué está “estable para demo” vs. experimental).

---

## 3. Ruta readaptada (prioridades)

La ruta anterior seguía priorizando features (metaplan, generative LLM, swarm). **Se ajusta** así:

| Prioridad | Enfoque | Objetivo |
|-----------|---------|----------|
| **P0** | **Perfiles de runtime** + tests de humo en CI | Reducir superficie accidental: demos y CI conocen **conjuntos de env** soportados (`src/runtime_profiles.py`). |
| **P1** | Persistencia de metas / markers (cuando toque) | Continuidad longitudinal alineada con snapshot y tests de round-trip. |
| **P2** | Generative / LLM local / metaplanning | Solo con criterios de aceptación y tests MalAbs claros. |
| **P3** | Swarm / P2P | Fuera del núcleo hasta modelo de amenazas explícito. |

**Próxima tarea ejecutada como cierre del hueco P0:** definición de `RUNTIME_PROFILES` y `tests/test_runtime_profiles.py` (incluido en `pytest tests/` por CI).

### 3.1 Orden de entrega recomendado (robustez → epistemología → demo)

1. **Robustez:** perfiles en `src/runtime_profiles.py` (`apply_runtime_profile` en tests); CI ejecuta `tests/test_runtime_profiles.py` junto con el resto de `tests/`; refuerzo de MalAbs / percepción en `tests/test_input_trust.py` con [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md).
2. **Epistemología:** KB lighthouse operativo y límites en [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md); tests en `tests/test_reality_verification.py` / `tests/test_lighthouse_kb_schema.py`.
3. **Demo / situado:** **cerrado** con perfil nominal **`situated_v8_lan_demo`** + guía [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md) (v8 + LAN sin hardware bruto); marco [`PROPUESTA_ORGANISMO_SITUADO_V8.md`](PROPUESTA_ORGANISMO_SITUADO_V8.md), pasos red [`LOCAL_PC_AND_MOBILE_LAN.md`](LOCAL_PC_AND_MOBILE_LAN.md).

---

## 4. Perfiles nominales (operadores y CI)

Los nombres y variables viven en código: **`src/runtime_profiles.py`**. Resumen:

| Perfil | Rol |
|--------|-----|
| `baseline` | Sin flags extra; línea base para regresión. |
| `judicial_demo` | Escalada judicial + tribunal mock + JSON judicial. |
| `hub_dao_demo` | Constitución HTTP pública + acciones DAO por WebSocket. |
| `nomad_demo` | Simulación HAL + auditoría de migración nómada. |
| `reality_lighthouse_demo` | Faro JSON (`KERNEL_LIGHTHOUSE_KB_PATH`) + JSON `reality_verification` en WebSocket; ejecutar desde raíz del repo. |
| `lan_mobile_thin_client` | `CHAT_HOST=0.0.0.0` para cliente móvil en la misma WiFi ([LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)). |
| `operational_trust` | UX “estoico” en WebSocket: sin homeostasis / monólogo / experience_digest — política del núcleo sin cambio ([POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md), Issue 5). |
| `lan_operational` | `lan_mobile_thin_client` + `operational_trust`: WiFi LAN con JSON mínimo narrativo ([KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md), Issue 7). |
| `moral_hub_extended` | Hub V12 ampliado: constitución pública + voto DAO + `deontic_gate` + auditoría de transparencia (Issue 7). |
| `situated_v8_lan_demo` | v8 situado: LAN + `KERNEL_SENSOR_*` (fixture + preset) + vitalidad / multimodal en JSON — [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md). |
| `perception_hardening_lab` | Endurecimiento Fase 1: tier léxico + cruce percepción + `D_delib` por incertidumbre + parse fail-local + `light_risk_tier` en WebSocket — [`PRODUCTION_HARDENING_ROADMAP.md`](PRODUCTION_HARDENING_ROADMAP.md), [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md). |
| `phase2_event_bus_lab` | Fase 2 (spike): bus de eventos in-process `KERNEL_EVENT_BUS` — [`adr/0006-phase2-core-boundary-and-event-bus.md`](../adr/0006-phase2-core-boundary-and-event-bus.md), [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md). |

**Política de flags (Issue 7):** familias de `KERNEL_*`, combinaciones **no recomendadas** y postura de deprecación — **[KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md)**.

**Experimental:** cualquier otra combinación de `KERNEL_*` se considera **no garantizada** hasta que se añada un perfil o un test dedicado.

**Pilar epistémico (V11+):** ver [PROPUESTA_VERIFICACION_REALIDAD_V11.md](PROPUESTA_VERIFICACION_REALIDAD_V11.md) — faro local vs premisas rivales (implementado); destilación y veto DAO (pendiente).

**Puente nomada PC–smartphone:** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — clases de hardware, capas de compatibilidad a desarrollar, smartphone como primera aproximación a percepción sensorial coordinada; red segura para campo bajo indicación del operador.

---

## 5. Backlog público (crítica técnica → issues)

Tras **dos** revisiones externas independientes (abril 2026), el proyecto publica un **deslinde honesto** y **siete ítems consolidados** (temas redundantes fusionados: p. ej. listas de texto + riesgo de **percepción GIGO** → un solo épico P0 de **confianza de entrada**). Incluye: núcleo documentado + *spike* de empaquetado pip, HCI/weakness en dominios críticos, política honesta **L0 inmutable vs borradores comunitarios**. Contenido listo para pegar como *GitHub Issues*:

- **[CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md)**

La landing [Roadmap](https://mosexmacchinalab.com/roadmap) resume el mismo track para socios y visitantes.

---

## 6. Referencias cruzadas

- [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) — snapshot de madurez por módulo y brechas conscientes (abril 2026).
- [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) — trazabilidad técnica reciente; la sección “Next development session” apunta aquí para la ruta.
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — persistencia y Fernet.
- [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) — mapa del hub.
- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) — política de variables `KERNEL_*` (Issue 7).
- [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) — roadmap **no vinculante** hacia endurecimiento de despliegue (fases 1–3); **síntesis de revisiones** (fortalezas, críticas, conclusiones); ronda documental cerrada — seguimiento en issues/ADRs.

---

*Ex Machina Foundation — documento vivo; alinear cambios de ruta con CHANGELOG y HISTORY.*
