# Estrategia, ruta y riesgos — Ethical Android MVP

Documento de **síntesis** (abril 2026): conclusiones de revisión del proyecto, expectativas realistas, **readaptación de la ruta**, y el **hueco principal** que prioriza el trabajo siguiente.

**Relación con otros docs:** el núcleo normativo y las capas advisory siguen descritos en [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) y [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). Las PROPUESTA en `docs/discusion/` son diseño; este archivo es **gobierno de producto / operación**.

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

**Experimental:** cualquier otra combinación de `KERNEL_*` se considera **no garantizada** hasta que se añada un perfil o un test dedicado.

**Pilar epistémico (V11+):** ver [PROPUESTA_VERIFICACION_REALIDAD_V11.md](discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md) — faro local vs premisas rivales (implementado); destilación y veto DAO (pendiente).

---

## 5. Referencias cruzadas

- [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) — trazabilidad técnica reciente; la sección “Next development session” apunta aquí para la ruta.
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — persistencia y Fernet.
- [discusion/UNIVERSAL_ETHOS_AND_HUB.md](discusion/UNIVERSAL_ETHOS_AND_HUB.md) — mapa del hub.

---

*Ex Machina Foundation — documento vivo; alinear cambios de ruta con CHANGELOG y HISTORY.*
