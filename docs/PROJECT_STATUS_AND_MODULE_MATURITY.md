# Estado del proyecto y madurez por módulo

**Actualización:** abril 2026 · **Tests:** `pytest` recoge **403** pruebas en el árbol `tests/`.

Este documento resume **dónde está** el Ethos Kernel MVP hoy y una lectura honesta de **madurez** por área (no sustituye ADRs ni `RUNTIME_CONTRACT.md`).

---

## 1. Dónde estamos (síntesis)

| Dimensión | Estado |
|-------------|--------|
| **Núcleo ético** | Pipeline MalAbs → buffer → Bayes → polos → voluntad; decisiones con tests de invariantes. |
| **Chat en tiempo real** | WebSocket `/ws/chat`, MalAbs texto + percepción validada (Pydantic/coherencia), capas advisory bajo flags. |
| **Confianza de entrada** | MalAbs léxico primero; capas semánticas opcionales (embeddings / árbitro LLM); percepción acotada y coherencia de campos. |
| **Modelo de usuario (ToM ligero)** | Fases A–C implementadas: patrones cognitivos, banda de riesgo, fase judicial para tono, persistencia en snapshot. |
| **Justicia / DAO (demo)** | Escalada por sesión, dossier mock, tribunal simulado opcional; gobernanza **off-chain** en este repo. |
| **Persistencia** | `KernelSnapshotV1` (schema v3 con campos nuevos compatibles hacia atrás), JSON opcionalmente Fernet. |
| **Operación** | Muchas variables `KERNEL_*`; perfiles nominales en `runtime_profiles.py`; política en `KERNEL_ENV_POLICY.md`. |

**Lectura:** el producto es un **runtime de demostración e investigación** con trazas auditables; no es un producto de moderación de contenido ni un sistema de certificación legal.

---

## 2. Leyenda de madurez

| Nivel | Significado |
|-------|-------------|
| **Sólido** | Cubierto por tests de regresión; contrato de uso claro en docs; camino principal estable. |
| **Demo** | Funcional para demos y desarrollo; requiere tuning de entorno o LLM; no prometer “producción” sin perfil. |
| **Experimental** | Tras `KERNEL_*` u opt-in; API o heurísticas pueden evolucionar. |
| **Stub / parcial** | Superficie narrativa o API presente; integración física o distribuida real fuera de alcance. |

---

## 3. Madurez por área (módulos y subsystems)

| Área | Archivos / entrada | Madurez | Notas |
|------|----------------------|---------|--------|
| **Kernel orchestration** | `kernel.py` (`process`, `process_chat_turn`, `process_natural`) | **Sólido** | Orquesta el grafo; tests de chat y natural. |
| **MalAbs (texto)** | `absolute_evil.py`, `input_trust.py` | **Sólido** | Lista + normalización; tests dedicados. |
| **MalAbs semántico** | `semantic_chat_gate.py`, `absolute_evil` capas | **Demo** | Depende de Ollama/embeddings; fallbacks documentados. |
| **Percepción LLM** | `llm_layer.py`, `perception_schema.py` | **Sólido** | Validación Pydantic, coherencia, fallback local. |
| **Bayes / buffer / polos** | `bayesian_engine.py`, `buffer.py`, `ethical_poles.py`, `pole_linear.py` | **Sólido** | Núcleo decisional con tests; polos lineales configurables (ADR 0004). |
| **Reflexión / saliencia / PAD** | `ethical_reflection.py`, `salience_map.py`, `pad_archetypes.py` | **Demo** | Lectura para auditoría y tono; no vetan acción. |
| **User model (ToM)** | `user_model.py` | **Demo** | Heurísticas + tono; persistido en snapshot; ver `USER_MODEL_ENRICHMENT.md`. |
| **Uchi–Soto** | `uchi_soto.py` | **Demo** | `tone_brief` hacia LLM; mezcla familiaridad + `trust_score`; perfiles persistidos; roster rico → [PROPUESTA_ROSTER…](discusion/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md). |
| **Roster social multi-agente** | — (diseño) | **No** | Propuesta: [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](discusion/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) (jerarquía, datos por cercanía, diálogo doméstico/íntimo advisory). |
| **Escalada judicial** | `judicial_escalation.py` | **Demo** | Sesión, strikes, vistas públicas; DAO mock, no red real. |
| **Memoria narrativa / identidad** | `narrative.py`, `narrative_identity.py` | **Sólido** | Episodios y digest; checkpoints. |
| **Tiempo subjetivo** | `subjective_time.py` | **Demo** | Continuidad en snapshot; efecto acotado. |
| **Cronobiología** | `subjective_time` + campos chat | **Demo** | Telemetría opcional. |
| **Sensores / multimodal / vitalidad** | `sensor_contracts`, `multimodal_trust`, `vitality.py` | **Demo** | Señales fusionadas; antispoof heurístico. |
| **Epistemic / reality / lighthouse** | `epistemic_dissonance.py`, `reality_verification.py` | **Experimental** | Tono y KB local; límites en docs. |
| **Generative candidates** | `generative_candidates.py` | **Experimental** | Acciones trazables; MalAbs igual. |
| **v10 operacional** | `metaplan_registry`, `somatic_markers`, `gray_zone_diplomacy` | **Experimental** | Flags; sin veto de política. |
| **DAO mock / hub / constitución** | `mock_dao.py`, `moral_hub`, `constitution` HTTP | **Demo** | Estado en JSON/SQLite según feature; auditoría tipo hub. |
| **Persistencia** | `persistence/schema.py`, `kernel_io.py`, `json_store.py` | **Sólido** | Round-trip testeado; migración v1→v3. |
| **Chat server** | `chat_server.py` | **Sólido** | Humo + integración en tests. |
| **Guardian Angel** | `guardian_mode.py` | **Experimental** | Opt-in; solo tono. |
| **Psi sleep / genoma** | `psi_sleep.py`, drift env | **Demo** | Límites de deriva testeados donde aplica. |

---

## 4. Brechas conscientes (no olvidadas)

1. **Superficie de configuración:** muchas `KERNEL_*`; la maturidad operativa depende de **perfiles** (`runtime_profiles.py`) y de documentación honesta.
2. **LLM ≠ garantía:** percepción y texto del modelo son **entradas acotadas**, no verdad de campo.
3. **Gobernanza:** DAO y tribunal en repo son **mock / demo**, no consenso distribuido real.
4. **Seguridad de despliegue:** checkpoint Fernet, bind LAN, etc. están documentados; endurecimiento “producción” sigue **roadmap aparte** (`PRODUCTION_HARDENING_ROADMAP.md`).

---

## 5. Referencias

- Estrategia y riesgos: [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md)
- Cadena de decisión: [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md)
- Contrato runtime: [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)
- Modelo de amenazas entrada: [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)
- Enriquecimiento user model: [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md)
- Changelog: [CHANGELOG.md](../CHANGELOG.md)

---

*Documento de orientación; alinear con cambios de código en CHANGELOG y tests.*
