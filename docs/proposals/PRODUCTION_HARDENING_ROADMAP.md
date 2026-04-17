# Roadmap de endurecimiento hacia despliegue serio (no vinculante)

**Estado:** **propuesta + síntesis** — complementa [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) y el backlog de crítica [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md). **No** sustituye el contrato runtime ni promete certificación “production” hasta criterios de aceptación y tests explícitos.

**Propósito:** capturar el **valor** de endurecer percepción, contratos de datos, modularización y UX honesta **sin** ocultar límites: el kernel sigue siendo un **MVP auditable**; cualquier capa nueva debe documentarse como **heurística** donde corresponda ([`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)).

---

## Qué ya cubre el repositorio (para no redundar)

| Tema | Dónde está |
|------|------------|
| Honestidad MalAbs / GIGO | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`SECURITY.md`](../SECURITY.md) |
| Percepción acotada + tests | `src/modules/llm_layer.py`, `tests/test_input_trust.py` |
| Percepción: informe de coerción + umbral **opt-in** → `D_delib` | `src/modules/perception_schema.py` (`PerceptionCoercionReport`), `src/kernel.py` (`KERNEL_PERCEPTION_UNCERTAINTY_*`), `tests/test_perception_coercion_report.py`, `tests/test_perception_uncertainty_delib.py` |
| Parse LLM +riesgo léxico + cruce (Fase 1) | `parse_perception_llm_raw_response`, `light_risk_classifier.py`, `perception_cross_check.py`, `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`, tests `test_perception_parse_contract.py` / `test_light_risk_classifier.py` / `test_perception_cross_check.py` |
| Lighthouse / duda epistémica (tono) | [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md), `reality_verification.py` |
| Perfiles runtime + CI | [`src/runtime_profiles.py`](../../src/runtime_profiles.py), `tests/test_runtime_profiles.py` |
| Frontera núcleo / empaquetado | [`adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md) |
| L0 vs DAO / borradores | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) |
| HCI / weakness | [`POLES_WEAKNESS_PAD_AND_PROFILES.md`](POLES_WEAKNESS_PAD_AND_PROFILES.md) |
| “Bayesian” = mezcla fija, no posterior completo | [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) Issue 1 + [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) |
| **Cuellos de botella / debilidades** (núcleo sync vs async, Ollama, MockDAO, naming) — inventario en inglés, un solo lugar | [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) |

No duplicar aquí párrafos largos sobre esos temas: mantener el detalle en ese archivo y usar este roadmap para fases y síntesis.

---

## Análisis núcleo–narrativa (abril 2026) — valor vs redundancia

Síntesis de revisión interna: **qué aporta** frente a lo ya dicho en el repo y **qué no duplicar**.

### Hallazgos funcionales

| Observación | ¿Aporta valor documental? | Redundancia / matiz |
|-------------|---------------------------|----------------------|
| **`BayesianEngine`** usa tres hipótesis con pesos fijos (`hypothesis_weights`, p. ej. `[0.4, 0.35, 0.25]`) que no se actualizan desde **`NarrativeMemory`** | **Sí** — explicita el *gap* “aprende narrativamente, no recalibra priors numéricamente”. | Issue 1 ya alinea **naming** y semántica; aquí el matiz nuevo es **usar episodios para pesos**, no solo renombrar. |
| **`EthicalPoles`** con fórmula lineal simple (`benefit * 0.6 + vulnerability * 0.4 - risk * 0.2` en heurística) y poco uso del **nombre** de la acción | **Sí** — deja claro el límite del MVP multipolar. | Coherente con multipolar explícito en teoría; no se vendió como modelo semántico profundo. |
| **MalAbs texto** vulnerable a **leet/variantes** (`b0mb`, `how 2`) | **Parcialmente redundante** con [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) (paráfrasis, homoglifos). | El ejemplo **leet** es un recordatorio útil para priorizar **normalización adicional** o capa opcional; no sustituye el aviso de “no infalible”. |
| **Percepción LLM** como punto único de fallo; JSON malo → señales por **defecto** cercanas a “calma” | **Sí** — riesgo de **GIGO silencioso**. | Parcialmente cubierto por clamps + tests + `epistemic_dissonance` en paralelo; **spike entregado:** informe de coerción + `uncertainty` en JSON de chat; **opt-in** `KERNEL_PERCEPTION_UNCERTAINTY_DELIB` puede promover `D_fast` → `D_delib` (no sustituye MalAbs ni un “segundo LLM auditor”). |

### Hallazgos arquitectónicos

| Observación | ¿Aporta valor documental? | Redundancia / matiz |
|-------------|---------------------------|----------------------|
| **`EthicalKernel.__init__`** acopla muchos módulos concretos; sin interfaces tipo `AbstractDAO` | **Sí** — refuerza la Fase 2 de este roadmap y el [ADR de empaquetado](adr/0001-packaging-core-boundary.md). | Ya se reconoce “mock” DAO; el valor es **formalizar contrato** cuando haya segundo implementador. |
| Señales sin **intervalo de confianza**; `epistemic_dissonance` compensa **en paralelo** | **Sí** — diseño futuro: incertidumbre **en** el vector de señales vs solo capa aparte. | Documentación honesta; implementación es investigación. |
| **`consequence_projection`** solo narrativo; no retroalimenta Bayes | **Sí** — alinea con contrato “teleología cualitativa, sin Monte Carlo” en v7. | No es bug si el producto no promete cerrar el bucle; cerrarlo sería **cambio de alcance**. |

### Registro de valor — spike de alto impacto relativo

**Propuesta:** usar **`NarrativeMemory`** (últimos *N* episodios, agrupados por **contexto** o similar) para derivar una **distribución empírica** de scores éticos y **ajustar `hypothesis_weights`** antes de cada evaluación bayesiana (con límites, suavizado y tests de no-regresión).

| Ventaja | Riesgo / condición |
|---------|---------------------|
| Pasa de estático a **experiencia→prior** sin inventar un LLM nuevo | Hay que evitar **deriva** no deseada y **sobreajuste** a sesgos del historial; reproducibilidad (`VariabilityEngine`, seeds). |
| Encaja con snapshot/persistencia de pesos ya existente | Requiere especificación: ventana *N*, decay, congelación por perfil operador. |

**Estado:** *registrado como dirección*; **no** implementado aquí. Encaja con Issue 1 (semántica bayesiana) y con [`HISTORY.md`](../HISTORY.md) / CHANGELOG si se hace spike.

---

## Revisión integral — fortalezas (registro de valor)

| Fortaleza | Por qué importa |
|-------------|-----------------|
| **Agencia ética computacional explícita** (filosofía, decisión, verificabilidad en tests) | Poco común en OSS; encaja con [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) y propósito del README. |
| **Modularidad con roles éticos claros** (Uchi–Soto, buffer, locus, Psi Sleep, etc.) | Facilita auditoría por módulo; tabla “quién fija `final_action`” en [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md). |
| **Documentación densa** (teoría, historia v1–v12, `docs/proposals/`, bibliografía) | Transparente académicamente; reduce “caja negra”. |
| **Varias superficies** (batch, WebSocket, dashboard estático, landing) | Demuestra runtime real sin acoplar un solo UI. |
| **Suite de tests grande** (invariantes, integración, persistencia) | Base para regresión; no sustituye validación externa (véase Issue 3 en crítica). |

---

## Revisión integral — críticas (valor vs redundancia)

| Crítica | Valor documental | Redundancia / matiz |
|---------|------------------|----------------------|
| **Sin “verdad ética” externa** — simulaciones no son mundo real | **Central y no redundante** como recordatorio. | Cubierto explícitamente por [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) **Issue 3** (piloto empírico); el criterio de “correcto” es **abierto por diseño** en filosofía aplicada. |
| **Complejidad** — ¿módulos críticos vs narrativa? | **Sí** — empuja a un “mapa de criticidad” para onboarding. | Parcialmente mitigado por [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md); módulos como Psi Sleep / weakness son **advisory** por contrato. |
| **LLM: percepción y comunicación como sesgo** | **Sí** — coherente con GIGO. | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) + capas de tono; no hay promesa de neutralidad del LLM. |
| **Persistencia** — corrupción, concurrencia, auditoría entre snapshots | **Sí** como *gaps de producto* si se promete HA multi-cliente. | [`RUNTIME_PERSISTENT.md`](RUNTIME_PERSISTENT.md) ya fija límites; tests de round-trip existen; **corrupción/concurrencia** son extensiones no obligatorias para MVP lab. |
| **Mock DAO / “governance” no on-chain** | **Sí** — evita hype. | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) y README ya enmarcan **mock / off-chain**. |
| **Input trust** — heurísticas no detalladas en README | **Parcial** — README enlaza `INPUT_TRUST`; matriz fina vive en docs. | Mejora posible: **una tabla resumida** en README (enlace profundo). |
| **API ad-hoc / muchos `KERNEL_*`** | **Sí** — fricción de integración. | [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) + perfiles; OpenAPI opcional con `KERNEL_API_DOCS` (véase política). |
| **Métricas de plataforma** (edad repo, nº issues) | **Baja** — cambian con el tiempo; **no** son indicadores de calidad del kernel. | Ignorar como evidencia en documentación estable. |
| **Sin benchmarks vs baselines** | **Sí**. | Issue 3 + sección “No objetivos” (no certificación por simulación sola). |
| **Branding** (slug repo vs Ethos Kernel vs lab) | **Sí** — barrera para nuevos lectores. | Registrar en README “Naming” o HISTORY; **no** exige renombrar repo de inmediato. |
| **ES/EN mezclados** | **Sí** para contribuciones globales. | Índice bilingüe o carpeta `docs/en/` como mejora incremental. |
| **Pocos ejemplos de diálogo “real”** | **Sí** — mejora pedagogía. | Casos de estudio = trabajo editorial; puede enlazarse a demos LAN. |

---

## Conclusiones para mejoras (síntesis operativa)

Estas conclusiones **no** sustituyen [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) ni el backlog; ordenan prioridades **después** de las rondas ya registradas (robustez técnica, epistemología lighthouse, demo v8).

### Corto plazo (mayor señal / menor fricción)

1. **Honestidad de alcance:** mantener visible que el núcleo es **MVP verificable en tests**, no “ética certificada” — README + Issue 3.
2. **Integración y operadores:** seguir densificando [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) y perfiles; considerar **tabla mínima** de `KERNEL_*` en README (enlaces a doc largo).
3. **Percepción:** marcar fallos de JSON / incertidumbre en pipeline (spikes ya listados en Fase 1 de este documento).
4. **Persistencia:** añadir tests **opt-in** de corrupción/concurrencia solo si un despliegue concreto lo exige (no bloquear lab).

### Mediano plazo

1. **Validación empírica** — Issue 3: protocolo de acuerdo con anotadores / expertos, **sin** confundir con verdad moral universal.
2. **Benchmarks comparativos** — definir baselines (reglas, LLM solo, kernel) y métricas **acordadas** (no “correctitud ética” única).
3. **Onboarding:** mapa “módulo → crítico vs advisory” derivado de `CORE_DECISION_CHAIN` + runtime contract.
4. **Language:** canonical filenames are `PROPOSAL_*.md` (English); `PROPUESTA_*.md` are legacy redirects. Spanish-only bodies (e.g. this roadmap) should gain short English summaries in the header or migrate to English over time.

### Largo plazo

1. **Gobernanza real** — solo si hay modelo de amenazas y necesidad; el repo **no** obliga blockchain.
2. **Certificación / auditoría externa** — marco posible; fuera del alcance del código actual salvo decisión de producto explícita.

### Reflexión (registro)

La tensión entre **formalismo verificable** y **ética situada** es inherente; el proyecto la asume mejor cuando documenta límites (simulaciones, mocks, heurísticas). El riesgo de “belleza interna sin impacto externo” se mitiga con **piloto empírico** y **benchmarks honestos**, no solo con más módulos.

---

## Fase 1 — Confianza de entrada y percepción (0–3 meses *orientativos*)

**Objetivo:** reducir GIGO y ataques triviales **sin** sustituir el núcleo normativo por un modelo opaco.

| Propuesta | Valor | Condiciones / riesgos |
|-----------|--------|------------------------|
| **Clasificador ligero opcional** (p. ej. etiquetas de riesgo, no generación de texto) **junto a** MalAbs por listas | Defensa en profundidad frente a paráfrasis; offline posible. | Dependencias, latencia, falsos positivos; debe ser **opt-in** (`KERNEL_*`), CI reproducible, y **no** “moderación infalible”. |
| **Contrato fuerte de salida LLM** (Pydantic / JSON Schema en APIs) | Fallo en validación antes de Bayes; alinea con percepción estructurada. | **Spike entregado:** `parse_perception_llm_raw_response` + códigos `parse_issues` en `coercion_report`; `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL` para fallos de parse; tests `test_perception_parse_contract.py`. Pydantic/coerción siguen siendo la capa numérica. |
| **Doble chequeo de percepción** (p. ej. discrepancia → `D_delib` o bandera de incertidumbre) | Coherente con crítica de percepción como vector de ataque. | **Spike entregado (sin segundo LLM):** `KERNEL_LIGHT_RISK_CLASSIFIER` + `KERNEL_PERCEPTION_CROSS_CHECK` marcan `cross_check_discrepancy` y suben `uncertainty` (combinable con `KERNEL_PERCEPTION_UNCERTAINTY_DELIB`); tests `test_light_risk_classifier.py`, `test_perception_cross_check.py`. |

**Enlace explícito al backlog:** Issue épico **input trust** en [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) (chat + percepción).

---

## Fase 2 — Arquitectura: núcleo vs extensiones (3–6 meses *orientativos*)

**Objetivo:** integraciones (p. ej. robótica) que solo necesiten **señales → decisión** sin arrastrar narrativa/DAO completa.

| Propuesta | Valor | Condiciones / riesgos |
|-----------|--------|------------------------|
| **Paquete `ethos-core` vs `ethos-extensions`** (o equivalente en monorepo) | Alineado con ADR de empaquetado; reduce acoplamiento. | Refactor grande; criterio: qué tests definen el **núcleo ético** vs telemetría. **Spike documental:** [`adr/0006-phase2-core-boundary-and-event-bus.md`](../adr/0006-phase2-core-boundary-and-event-bus.md), [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md). |
| **Bus de eventos local (pub/sub)** para memoria, DAO, PAD, etc. | Aislar fallos de subsistemas secundarios. | **Spike incremental entregado:** `KernelEventBus` síncrono opt-in (`KERNEL_EVENT_BUS`), eventos `kernel.decision` y `kernel.episode_registered`; ver ADR 0006, `src/modules/kernel_event_bus.py`, `tests/test_kernel_event_bus.py`, perfil `phase2_event_bus_lab`. Async / multiproceso sigue **fuera** de alcance. |

---

## Fase 3 — UX y constitución (6+ meses *orientativos*)

**Objetivo:** confianza humana y gobernanza auditables **sin** dictar filosofía desde un solo archivo opaco.

| Propuesta | Valor | Condiciones / riesgos |
|-----------|--------|------------------------|
| **Debilidad → transparencia epistémica** (límites de modelo/sensores en lugar de “emoción simulada” en dominios críticos) | Coherente con HCI honesto (Issue 5). | Cambio de copy + contrato de producto; no solo refactor de `weakness_pole`. |
| **L0 externalizado** (YAML/JSON versionado) | Auditoría sin leer Python; base para firmas/DAO futuras. | Tensiona “L0 en código” hoy; requiere **modelo de amenazas**, migración y tests de carga idéntica. |

---

## No objetivos (explícitos)

- Sustituir MalAbs o el buffer por un **único** clasificador ML sin trazabilidad y tests de regresión.
- Prometer **seguridad absoluta** o moderación infalible (véase [`SECURITY.md`](../SECURITY.md)).
- Confundir este documento con un **compromiso comercial** de SLA o certificación.

---

## Cierre de la ronda de propuestas (documental)

Las entradas **“producción v2”**, **núcleo–narrativa** y **revisión integral (fortalezas / críticas / conclusiones)** quedan **archivadas** en este archivo como registro único. Nuevas ideas de producto deberían abrir **issues** o ADRs específicos; no duplicar aquí listas largas salvo síntesis.

Para cambios de alcance o spikes de código: [`CHANGELOG.md`](../CHANGELOG.md) + PR.

---

## Referencias cruzadas

- [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) — prioridades P0–P3 y orden robustez → epistemología → demo (§3.1).
- [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) — combinaciones de flags.
- [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) — pipeline normativo.

*Documento vivo — alinear cambios sustantivos con HISTORY/CHANGELOG cuando se ejecuten spikes o se cierren fases.*
