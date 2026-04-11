# `docs/proposals/` — diseño, teoría y operación

Material de **referencia** y **exploración**: propuestas versionadas, contratos de runtime, mapas teoría ↔ código, guías de operador y hilos de diseño. **No** sustituye al backlog de issues ni al README raíz del producto.

Este directorio es el **único** lugar unificado para lo que antes estaba en `docs/discusion/`, `docs/experimental/` y varios `docs/*.md` sueltos. Las **ADR** siguen en [`docs/adr/`](../adr/README.md). Recursos gráficos: [`docs/multimedia/`](../multimedia/README.md).

---

## Novedades (abril 2026)

Resumen de lo más reciente alineado con el código y la documentación; el detalle cronológico está en [`CHANGELOG.md`](../../CHANGELOG.md).

| Área | Qué hay de nuevo |
|------|------------------|
| **Docs** | Carpeta única **`docs/proposals/`**; enlaces del repo apuntan aquí. ADR y plantillas no se movieron. |
| **Uchi–Soto (roster)** | **Fase 3** en kernel: `RelationalTier`, EMA de confianza sensorial, buffer de olvido, `linked_peer_ids`, integración en `process` / chat. Ver [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md). |
| **Modelo de usuario** | Enriquecimiento fases A–C: patrón cognitivo, banda de riesgo, fase judicial y checkpoint; persistencia en snapshot. Ver [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md). |
| **Tiempo / Bayes** | Prior de horizonte temporal (mezcla bayesiana, ADR 0005). Ver [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md). |
| **Percepción** | Validación con Pydantic, coherencia y fallback local. Ver [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md). |
| **Estado del MVP** | Tabla de madurez por módulo y brechas. Ver [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md). |
| **Marca / multimedia** | Logo canónico [`docs/multimedia/media/logo.png`](../multimedia/media/logo.png); índice en [README multimedia](../multimedia/README.md). |

---

## Por dónde empezar

| Si buscas… | Abre |
|------------|------|
| Mapa teoría ↔ implementación y tests | [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) |
| Contrato de runtime (inglés) | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
| Snapshot y persistencia | [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) |
| Fases / migración runtime | [RUNTIME_PHASES.md](RUNTIME_PHASES.md), [RUNTIME_FASES.md](RUNTIME_FASES.md) (español) |
| Estado actual del kernel | [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) |
| Referencia rápida operador | [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) |

---

## Propuestas versionadas (línea v6–v12 y anexos)

| Documento | Tema |
|-----------|------|
| [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md) | Autorreferencia / GWT / drives / narrativa (v6) — *español* |
| [PROPUESTA_INTEGRACION_APORTES_V6.md](PROPUESTA_INTEGRACION_APORTES_V6.md) | Fases coherentes, inventario de modelo, exclusiones — *español* |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Cinco pilares, estado MVP por pilar, hilos abiertos — *español* |
| [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) | ToM ligera, cronobiología, premisas, teleología cualitativa — *español* |
| [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) | Organismo situado: fusión sensorial, vitalidad, agencia, hardware — *español* |
| [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md) | Extensión v8: vitalidad, sacrificio, cierre digno, legado narrativo — *español* |
| [DEMO_SITUATED_V8.md](DEMO_SITUATED_V8.md) | Demo / situación v8 |
| [PROPUESTA_ANGEL_DE_LA_GUARDIA.md](PROPUESTA_ANGEL_DE_LA_GUARDIA.md) | Modo ángel de la guarda (tono; sin segundo veto) — *español* |
| [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | Pilares v9 (epistémico, generativo, enjambre, metaplanificación) — *español* |
| [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md) | v10 operativa: diplomacia, skills, marcadores somáticos — *español* |
| [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) | Gobernanza V11, auditoría DAO, roadmap — *inglés* en fases clave |
| [PROPUESTA_VERIFICACION_REALIDAD_V11.md](PROPUESTA_VERIFICACION_REALIDAD_V11.md) | Verificación de realidad (diseño) |
| [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](PROPUESTA_ESTADO_ETOSOCIAL_V12.md) | Registro V12, variables de entorno, arquitectura unificada |
| [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) | Roster multiagente, tiers Uchi–Soto, buffer de olvido, Fase 3 implementada |
| [PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md](PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md) | Alertas DAO y transparencia |
| [PROPUESTA_CONCIENCIA_NOMADA_HAL.md](PROPUESTA_CONCIENCIA_NOMADA_HAL.md) | Instanciación nómada, HAL, serialización existencial — *español* |
| [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) | Visión hub ↔ código, capas UniversalEthos, mapa de módulos — *inglés* |

---

## Runtime, entorno y cadena de decisión

| Documento | Tema |
|-----------|------|
| [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) | Contrato de runtime |
| [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) | Persistencia (inglés) |
| [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md) | Persistencia (español) |
| [RUNTIME_PHASES.md](RUNTIME_PHASES.md) | Fases del runtime |
| [RUNTIME_FASES.md](RUNTIME_FASES.md) | Fases (español) |
| [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) | Política de variables de entorno |
| [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) | Cadena de decisión del núcleo |

---

## Gobernanza, modelo de usuario y capas semánticas

| Documento | Tema |
|-----------|------|
| [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md) | MockDAO y capa L0 |
| [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) | Enriquecimiento del modelo de usuario (judicial, cognitivo, riesgo) |
| [LIGHTHOUSE_KB.md](LIGHTHOUSE_KB.md) | Knowledge base Lighthouse |
| [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) | Capas semánticas MALABS |

---

## Percepción, polos, tiempo y confianza de entrada

| Documento | Tema |
|-----------|------|
| [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) | Validación de percepción (Pydantic, coherencia) |
| [POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md) | Polos, debilidad, PAD y perfiles |
| [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) | Prior temporal por horizontes (ADR 0005) |
| [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) | Modelo de amenazas de confianza en entradas / telemetría advisory |

---

## Infraestructura local, LLM y nómada

| Documento | Tema |
|-----------|------|
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | PC local y LAN móvil |
| [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) | Puente PC–smartphone nómada |
| [LLM_STACK_OLLAMA_VS_HF.md](LLM_STACK_OLLAMA_VS_HF.md) | Ollama vs Hugging Face |

---

## Estrategia, endurecimiento y trazabilidad

| Documento | Tema |
|-----------|------|
| [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) | Estrategia y ruta |
| [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) | Roadmap de endurecimiento hacia despliegue |
| [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) | Crítica, roadmap e issues |
| [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) | Estado del proyecto y madurez por módulo |
| [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) | Trazabilidad reciente (Guardian, v9–v10) ↔ bibliografía |
| [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) | Referencia rápida para operadores |

---

## Pilotos empíricos y amenazas P2P

| Documento | Tema |
|-----------|------|
| [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md) | Metodología de piloto empírico |
| [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md) | Protocolo de piloto |
| [SWARM_P2P_THREAT_MODEL.md](SWARM_P2P_THREAT_MODEL.md) | Modelo de amenazas enjambre P2P |

---

## Conciencia, afecto y experimentación (no contrato vivo)

| Documento | Tema |
|-----------|------|
| [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) | Arquetipos experimentales conciencia/afecto |
| [PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md](PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md) | Borrador tipo paper (afecto, fenómenos, hipótesis) — *español* |

---

## Relación con el resto del repositorio

- **Decisiones de arquitectura:** [`docs/adr/`](../adr/README.md)  
- **Cambios versionados:** [`CHANGELOG.md`](../../CHANGELOG.md)  
- **Contexto histórico narrativo:** [`HISTORY.md`](../../HISTORY.md)  
- **Bibliografía:** [`BIBLIOGRAPHY.md`](../../BIBLIOGRAPHY.md)  
- **Producto y desarrollo:** [README raíz](../../README.md)

