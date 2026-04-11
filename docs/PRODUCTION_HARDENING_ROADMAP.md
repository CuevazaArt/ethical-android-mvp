# Roadmap de endurecimiento hacia despliegue serio (no vinculante)

**Estado:** **propuesta + síntesis** — complementa [`ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md) y el backlog de crítica [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md). **No** sustituye el contrato runtime ni promete certificación “production” hasta criterios de aceptación y tests explícitos.

**Propósito:** capturar el **valor** de endurecer percepción, contratos de datos, modularización y UX honesta **sin** ocultar límites: el kernel sigue siendo un **MVP auditable**; cualquier capa nueva debe documentarse como **heurística** donde corresponda ([`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)).

---

## Qué ya cubre el repositorio (para no redundar)

| Tema | Dónde está |
|------|------------|
| Honestidad MalAbs / GIGO | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`SECURITY.md`](../SECURITY.md) |
| Percepción acotada + tests | `src/modules/llm_layer.py`, `tests/test_input_trust.py` |
| Lighthouse / duda epistémica (tono) | [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md), `reality_verification.py` |
| Perfiles runtime + CI | [`src/runtime_profiles.py`](../src/runtime_profiles.py), `tests/test_runtime_profiles.py` |
| Frontera núcleo / empaquetado | [`adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md) |
| L0 vs DAO / borradores | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) |
| HCI / weakness | [`POLES_WEAKNESS_PAD_AND_PROFILES.md`](POLES_WEAKNESS_PAD_AND_PROFILES.md) |
| “Bayesian” = mezcla fija, no posterior completo | [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) Issue 1 + [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) |

---

## Análisis núcleo–narrativa (abril 2026) — valor vs redundancia

Síntesis de revisión interna: **qué aporta** frente a lo ya dicho en el repo y **qué no duplicar**.

### Hallazgos funcionales

| Observación | ¿Aporta valor documental? | Redundancia / matiz |
|-------------|---------------------------|----------------------|
| **`BayesianEngine`** usa tres hipótesis con pesos fijos (`hypothesis_weights`, p. ej. `[0.4, 0.35, 0.25]`) que no se actualizan desde **`NarrativeMemory`** | **Sí** — explicita el *gap* “aprende narrativamente, no recalibra priors numéricamente”. | Issue 1 ya alinea **naming** y semántica; aquí el matiz nuevo es **usar episodios para pesos**, no solo renombrar. |
| **`EthicalPoles`** con fórmula lineal simple (`benefit * 0.6 + vulnerability * 0.4 - risk * 0.2` en heurística) y poco uso del **nombre** de la acción | **Sí** — deja claro el límite del MVP multipolar. | Coherente con multipolar explícito en teoría; no se vendió como modelo semántico profundo. |
| **MalAbs texto** vulnerable a **leet/variantes** (`b0mb`, `how 2`) | **Parcialmente redundante** con [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) (paráfrasis, homoglifos). | El ejemplo **leet** es un recordatorio útil para priorizar **normalización adicional** o capa opcional; no sustituye el aviso de “no infalible”. |
| **Percepción LLM** como punto único de fallo; JSON malo → señales por **defecto** cercanas a “calma” | **Sí** — riesgo de **GIGO silencioso**. | Parcialmente cubierto por clamps + tests + `epistemic_dissonance` en paralelo; el gap es **marcar explícitamente incertidumbre de percepción** en el pipeline (spike futuro). |

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

## Fase 1 — Confianza de entrada y percepción (0–3 meses *orientativos*)

**Objetivo:** reducir GIGO y ataques triviales **sin** sustituir el núcleo normativo por un modelo opaco.

| Propuesta | Valor | Condiciones / riesgos |
|-----------|--------|------------------------|
| **Clasificador ligero opcional** (p. ej. etiquetas de riesgo, no generación de texto) **junto a** MalAbs por listas | Defensa en profundidad frente a paráfrasis; offline posible. | Dependencias, latencia, falsos positivos; debe ser **opt-in** (`KERNEL_*`), CI reproducible, y **no** “moderación infalible”. |
| **Contrato fuerte de salida LLM** (Pydantic / JSON Schema en APIs) | Fallo en validación antes de Bayes; alinea con percepción estructurada. | Ya hay clamp en código; el salto es **esquema + errores explícitos** + tests. |
| **Doble chequeo de percepción** (p. ej. discrepancia → `D_delib` o bandera de incertidumbre) | Coherente con crítica de percepción como vector de ataque. | El auditor no puede ser “otro LLM sin límites”; definir umbrales y tests. |

**Enlace explícito al backlog:** Issue épico **input trust** en [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) (chat + percepción).

---

## Fase 2 — Arquitectura: núcleo vs extensiones (3–6 meses *orientativos*)

**Objetivo:** integraciones (p. ej. robótica) que solo necesiten **señales → decisión** sin arrastrar narrativa/DAO completa.

| Propuesta | Valor | Condiciones / riesgos |
|-----------|--------|------------------------|
| **Paquete `ethos-core` vs `ethos-extensions`** (o equivalente en monorepo) | Alineado con ADR de empaquetado; reduce acoplamiento. | Refactor grande; criterio: qué tests definen el **núcleo ético** vs telemetría. |
| **Bus de eventos local (pub/sub)** para memoria, DAO, PAD, etc. | Aislar fallos de subsistemas secundarios. | Orden, determinismo y tests síncronos actuales; diseño incremental (no reescritura big-bang). |

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

## Próximas propuestas

*Espacio reservado para la **última** ronda de diseño por incorporar* (revisión externa, socio técnico o fork de producto). El análisis de núcleo–narrativa (arriba) y el roadmap por fases quedan **cerrados como registro** hasta nueva entrada.

Al añadir una propuesta:

1. Indicar **qué fase** toca y **qué documentos del repo** actualiza o contradice.
2. Añadir enlace en [`CHANGELOG.md`](../CHANGELOG.md) si hay decisión de alcance o spike de código.

---

## Referencias cruzadas

- [`ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md) — prioridades P0–P3 y orden robustez → epistemología → demo (§3.1).
- [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) — combinaciones de flags.
- [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) — pipeline normativo.

*Documento vivo — alinear cambios sustantivos con HISTORY/CHANGELOG cuando se ejecuten spikes o se cierren fases.*
