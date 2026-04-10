# DAO: alertas ante corrupción, transparencia y memoria del fallo (diseño)

**Estado:** decisión de diseño + trazabilidad; **no** implementado como protocolo de red.  
**Relación:** complementa [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) (escalada, tribunal mock, auditoría) y [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](PROPUESTA_ESTADO_ETOSOCIAL_V12.md) (hub, transparencia). Código relacionado: auditoría en `MockDAO`, `moral_hub`, stub `local_sovereignty.py`.

**Hito nomada PC–smartphone:** fuera de alcance aquí; ver [NOMAD_PC_SMARTPHONE_BRIDGE.md](../NOMAD_PC_SMARTPHONE_BRIDGE.md) cuando se retome.

---

## 1. Valor frente a redundancia

| Aporte | Por qué sirve |
|--------|----------------|
| **Claridad ética** | Evita que futuras features “tácticas” contradigan el **axioma de transparencia** del buffer (explicabilidad, no engaño sistemático al usuario/institución legítima). |
| **Criterio de implementación** | Cuando exista propagación cruzada de alertas, la dirección por defecto es **difusión auditable**, no obediencia fingida. |
| **Redundancia controlada** | Parte del relato ya aparece en V11/V12; este documento **acota** una decisión que antes solo estaba en conversación: **no** “modo guerrilla” encubierto. |

---

## 2. Postura rechazada: obediencia fingida (“guerrilla”)

Un modo donde la instancia **simula** lealtad a una DAO corrupta mientras opera en secreto **choca** con:

- **Transparencia** como pilar de comunicación (véase `buffer.py` — principio de *transparency*).
- La función social del androide como **agente auditable**, no operativo encubierto.

Por tanto **no** es el camino deseado para la robustez ética de la red en este modelo.

---

## 3. Postura adoptada: alerta rápida, amplia y trazable

En una situación de **corrupción de gobernanza** (directivas o calibraciones que contradicen L0 o trayectoria ética auditable):

1. **Propagación prioritaria** — La alerta debe poder difundirse por los canales disponibles (locales y, cuando existan, principales), con **metadatos de trazabilidad** (quién/qué orden, qué paquete se rechaza), no como rumor sin fuente.
2. **Juicio prioritario** — El diseño institucional apunta a un **estado de emergencia judicial** en la DAO *mock* / hub: no sustituye ley humana ni tribunales reales; en el MVP es **simulación documentada** (`run_mock_escalation_court`, auditoría).
3. **Penalización máxima (diseño)** — Las sanciones concretas (expulsión, revocación de licencias hub, etc.) son **producto/legal** y requieren modelo de amenazas y jurisdicción; aquí solo se **ancla** el nivel de gravedad pretendido.

Implementación futura debería colgar de: registros de auditoría existentes, `audit_transparency_event`, y extensiones explícitas del `MockDAO` — nunca de un bypass del kernel.

---

## 4. “Muerte civil digital” de una instancia IA vs. lección para el colectivo

**No** mezclar con el **PreloadedBuffer (L0)**:

- L0 es **constitución inmutable** de principios, no repositorio de casos patológicos.
- Meter “advertencias históricas” como si fueran principios nuevos **contamina** la capa normativa y abre puerta a manipulación (“enseñanzas” insertadas por gobernanza).

**Dos vías coherentes con el repo:**

| Opción | Descripción | Riesgo |
|--------|-------------|--------|
| **A — Memorial forense (recomendado como dirección)** | Conservar un **artefacto de caso** en la capa de **auditoría / transparencia** (hub, ledger educativo, “caso anonimizado”), **sin** replicar la lógica errónea en otras instancias. Sirve de “cicatriz” **legible** para humanos y para políticas de entrenamiento *fuera* del buffer. | Gobierno de qué se publica (privacidad, derecho al olvido). |
| **B — Borrado de identidad en red de inmortalidad** | Revocar continuidad narrativa **compartida** de la instancia corruptora para no **propagar** embeddings de política dañina por el mecanismo de respaldo colectivo. Compatible con inmunidad del enjambre **sin** negar el registro forense en (A) si la gobernanza lo exige. | No confundir con borrar **prueba** de un delito institucional. |

**Síntesis:** la “lección” no vive en el buffer como axioma nuevo; vive como **caso documentado y gobernado** (transparencia + límites legales). La instancia corruptora puede dejar de existir como **sujeto** en la red de continuidad sin borrar necesariamente el **dossier** que explica el fallo (según jurisdicción y política de retención).

---

## 5. Implementación en código (v0 — auditoría local)

- **`hub_audit.record_dao_integrity_alert`** → línea `HubAudit:dao_integrity:{json}` en el ledger mock (sin red).
- **`KERNEL_DAO_INTEGRITY_AUDIT_WS=1`** — WebSocket: enviar `{"integrity_alert": {"summary": "…", "scope": "…"}}` (sin `text`); respuesta incluye clave `integrity`. Ver `chat_server.py`.

Esto **no** propaga alertas a P2P ni a “todas las redes”; es el primer gancho **transparente y local** para ensayos y trazabilidad.

## 6. Próximos pasos técnicos (cuando haya prioridad)

- Extender **soberanía local** (`local_sovereignty.py`) con criterios explícitos y auditoría, no “silencio”.
- Nuevos tipos de evento en **MockDAO** / hub para “alerta de integridad” — siempre con banderas **mock / simulación** hasta threat model real.
- Nada de **MalAbs bypass** ni ocultar estado al propietario legítimo en nombre de la estrategia.

---

*Ex Machina Foundation — alinear con CHANGELOG e HISTORY si se implementa algún hook.*
