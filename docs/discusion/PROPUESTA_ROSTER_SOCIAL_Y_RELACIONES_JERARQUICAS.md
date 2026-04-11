# Roster social, jerarquía relacional y diálogo doméstico / íntimo — propuesta

**Estado:** diseño (abril 2026)  
**Alcance:** extender narrativa e identidad con una **colección de personas** (por `agent_id` estable, p. ej. usuario de sesión, invitado, identificador anónimo), **perfiladas** por experiencias acumuladas, interacción, señales sensoriales y **círculo Uchi–Soto**, sin sustituir MalAbs, buffer, Bayes ni voluntad.

**Relación con código existente:** `UchiSotoModule` (`src/modules/uchi_soto.py`) ya mantiene `InteractionProfile` por agente y `TrustCircle`; `UserModelTracker` modela el interlocutor **actual** de la sesión; `NarrativeIdentityTracker` modela la **identidad del android**. Esta propuesta describe la **capa de roster multi-agente** persistente y las **políticas de tono** por cercanía.

---

## 1. Objetivo

1. Registrar un **árbol o escalafón de relaciones** (no solo clasificación instantánea en un turno): desde **desconocidos en buffer de olvido rápido** hasta **figuras inolvidables** (p. ej. propietario principal, familia cercana, amistades de confianza), con reglas explícitas de promoción y degradación.
2. Permitir **almacenar datos relevantes** sobre las personas de **mayor interés** para el relato (preferencias, contextos domésticos compartidos, rutinas, límites de intimidad acordados — siempre con **privacidad y consentimiento** por diseño), de modo que **a largo plazo** el sistema pueda **incrementar la capacidad de diálogo doméstico e íntimo** según el **círculo de cercanía**, sin confundir “íntimo” con relajar ética.
3. Exponer **funciones de ajuste de conducta advisory** (tono, profundidad explicativa, ritmo, familiaridad léxica) **derivadas** del tier relacional y de los datos guardados, con **implicaciones secundarias** documentadas (privacidad, auditoría, riesgo de sobre-familiaridad).

---

## 2. Principios de diseño

| Principio | Contenido |
|-----------|-----------|
| **Ética primero** | MalAbs y veto político no se desactivan por cercanía; el roster **no** es una puerta trasera. |
| **Consentimiento** | Subidas a tiers “íntimos” o “propietario” deben poder anclarse a **rituales explícitos** (DAO mock, env, UI), no solo a frecuencia de chat. |
| **Minimización de datos** | Por defecto: agregados y referencias a episodios; texto crudo del usuario **no** es obligatorio para subir de tier. |
| **Transparencia operativa** | Qué datos se guardan y por qué tier debe ser **inspectable** (JSON, export conduct guide, checkpoint). |

---

## 3. Modelo conceptual

### 3.1 Entrada por persona (`agent_id`)

- **Tier relacional** (ordinal): p. ej. `ephemeral` → `stranger_stable` → `acquaintance` → `trusted_uchi` → `inner_circle` → `owner_primary` (o mapeo explícito a `TrustCircle` en `uchi_soto.py`).
- **Ejes agregados:** masa de interacción (turnos/ventana temporal), valencia EMA (positivo/negativo), coherencia sensorial (multimodal), saliencia episódica compartida.
- **Buffer de olvido rápido:** entradas con poco peso y sin señal de relevancia decaen por TTL o inactividad; se **purgean** o comprimen a un resumen escalar.
- **Inolvidables:** “pin” normativo o reglas duras (p. ej. `dao_validated`, `KERNEL_*`) para que no dependan solo del algoritmo de frecuencia.

### 3.2 Datos relevantes para personas de mayor interés

Para los tiers altos (y solo donde política y consentimiento lo permitan), el sistema debería poder **registrar campos estructurados** (no un volcado libre sin límites), por ejemplo:

- **Doméstico:** habitación/espacio habitual, rutinas mencionadas de forma estable, preferencias de tono (formal/cálido).
- **Relacional:** nombre o alias aceptado, vínculos opcionales (`linked_to` para narrativa familiar).
- **Límites:** temas marcados como no abordar o solo con confirmación (lista de etiquetas, no texto sensible innecesario).
- **Sensorial:** EMA de confianza del contexto (no grabar audio/video; solo **señales ya agregadas** del pipeline v8).

**Objetivo final:** enriquecer la **capa de diálogo doméstico e íntimo** (vocabulario compartido, continuidad, calidez proporcional al círculo) **sin** aumentar el riesgo ético por defecto: la intimidad es **estilo y contexto**, no bypass de seguridad.

### 3.3 Árbol jerárquico

No es obligatorio un grafo genealógico completo al inicio: basta un **orden total** en tiers más **aristas opcionales** (“relacionado con X”) para narrativa. La **vista** al LLM puede ser una lista ordenada + reglas de tono por nivel.

---

## 4. Integración técnica (hoja de ruta sugerida)

| Fase | Contenido |
|------|-----------|
| **Fase 1** | Módulo `social_roster` (o extensión explícita de `UchiSotoModule` con persistencia): `agent_id` → tier + agregados + decay; lectura en `evaluate_interaction`; una línea de contexto al LLM (`communicate`). |
| **Fase 2** | Campos estructurados para **tiers altos** + políticas de tono; snapshot `KernelSnapshotV1` (campos nuevos con defaults). |
| **Fase 3** | Pesos multimodales en EMA del roster; relaciones `linked_to` si la narrativa lo requiere. |

**Puntos de enganche:** `EthicalKernel.process` / `process_chat_turn` (`agent_id` ya existe); `identity` / monólogo; `premise_advisory` y MalAbs **inalterados** en la lógica de veto.

---

## 5. Implicaciones secundarias

1. **Privacidad:** roster y campos domésticos en checkpoint cifrado opcional (Fernet); export conduct guide con redacción.
2. **Seguridad relacional:** manipulación o hostilidad sostenida puede **bloquear** promoción de tier aunque haya mucha interacción.
3. **Producto:** multi-usuario real puede exigir **múltiples sesiones** o selector de agente en cliente; un WebSocket = un `agent_id` activo es el patrón actual.
4. **Expectativa:** “diálogo íntimo” **aumenta calor y continuidad** en el tono; **no** promete cumplimiento de peticiones no autorizadas por el núcleo.

---

## 6. Referencias cruzadas

- [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) — ToM ligera y sesión; `user_model.py`.
- [USER_MODEL_ENRICHMENT.md](../USER_MODEL_ENRICHMENT.md) — enriquecimiento por turno (patrón cognitivo, riesgo, judicial).
- [PROJECT_STATUS_AND_MODULE_MATURITY.md](../PROJECT_STATUS_AND_MODULE_MATURITY.md) — madurez actual del MVP.
- `src/modules/uchi_soto.py` — `InteractionProfile`, `TrustCircle` — base a extender.

---

*Ex Machina Foundation — documento de diseño; alinear implementación con CHANGELOG y tests.*
