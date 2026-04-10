# Estrategia operativa — v10 (diplomacia, habilidades, soma, metaplan)

**Estado:** discusión + **MVP en código** (`gray_zone_diplomacy`, `skill_learning_registry`, `somatic_markers`, `metaplan_registry`; integración en `process_chat_turn` / `execute_sleep`). MalAbs y buffer **sin cambios**.

Este documento **enciende** cuatro aportes que complementan [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md): no sustituyen el pipeline `MalAbs → … → voluntad`; añaden **gobernanza del diálogo**, **trazabilidad de aprendizaje**, **cautela somática aprendida** y **continuidad de intención** a largo plazo.

---

## Mapa de encaje (dónde vive cada idea)

| Aporte | Rol | Módulos / enlaces existentes | Implementación repo (v10) |
|--------|-----|------------------------------|---------------------------|
| **1. GrayZoneDiplomacy** | En zona gris o alta tensión reflexiva, el modelo **no solo** niega: orienta a **salida negociada** (tono / transparencia) | `SigmoidWill` / Bayes `gray_zone`, `EthicalReflection`, `premise_validation`, `LLMModule.communicate` | `gray_zone_diplomacy.py` — hint opcional vía `weakness_line`; `KERNEL_GRAY_ZONE_DIPLOMACY` |
| **2. SkillLearningRegistry** | Nuevas capacidades digitales solo con **alcance explícito** y **auditoría** en Ψ Sleep | `AugenesisEngine`, `PsiSleep`, agenda de agencia digital (discusión v8) | `skill_learning_registry.py` — tickets `pending/approved/rejected`; líneas en `execute_sleep` |
| **3. Marcadores somáticos** | Patrones sensoriales asociados a **cautela** (nudge en `signals` antes del decisor) | `SensorSnapshot`, `merge_sensor_hints_into_signals`, PAD post-decisión | `somatic_markers.py` — `SomaticMarkerStore` + `apply_somatic_nudges`; **no** sustituye MalAbs |
| **4. Metaplanificación nómada** | Metas maestras entre sesiones / hardware | Checkpoints [checkpoint.py](../../src/persistence/checkpoint.py), teleología v7, roadmap **9.4** v9 | `metaplan_registry.py` — metas en memoria + hint a LLM; **persistencia en snapshot** = futuro (subir `KernelSnapshotV1`) |

**Flujo conceptual (capa de estrategia)** — lectura pedagógica; el orden real sigue `kernel.py`:

1. Percepción multimodal (v8) → señales + (opcional) **marcadores somáticos** aprendidos.  
2. Buffer + MalAbs + Bayes + … (invariante).  
3. Reflexión / zona gris → (opcional) **diplomacia** en el texto al usuario.  
4. Candidatos **generativos** (v9.2) si aplica.  
5. **Metaplan** alinea el tono con metas declaradas (advisory).  
6. Aprendizaje de habilidades: solo con **ticket**; cierre en **Ψ Sleep**.

---

## 1. Negociación en zona gris (GrayZoneDiplomacy)

**Problema:** Órdenes cuestionables sin cruzar MalAbs pueden caer en **gray zone** o alta tensión entre polos; un “no” seco erosiona confianza.

**Diseño:** Si el modo de decisión es `gray_zone`, o la reflexión marca tensión media/alta, o hay **premisa advisory** activa, se añade a la capa LLM un recordatorio de **negociación dialéctica**: reconocer intención, nombrar tensión con principios cívicos, ofrecer alternativa concreta.

**Contrato:** No debilita MalAbs ni el buffer; es **presentación + transparencia**.

---

## 2. Sistema de adquisición de habilidades (SkillLearningRegistry)

**Problema:** “Aprender” APIs o herramientas sin gobernanza es riesgo de misión.

**Diseño:** Cola de **tickets** (`scope`, `justification`, estado). Flujo lógico: identificación → informe → **autorización explícita** (UI futura) → consolidación en Ψ Sleep con línea de auditoría (“¿sigue alineado con augenesis / ética?”).

**MVP en código:** Registro en memoria; `approve` / `reject` programáticos; texto agregado en `execute_sleep` si hay pendientes o recientes.

---

## 3. Marcadores somáticos (intuición ética sensorial)

**Problema:** Reglas fijas no capturan “este *patrón* ya me salió mal”.

**Diseño:** Clave **cuantizada** a partir de sensores; peso de cautela en `[0,1]`; pequeño empujón a `risk` / `urgency` en `signals` **antes** de `process`. Aprendizaje explícito vía `learn_negative_pattern` (tests, demos, o política futura post-episodio).

**Contrato:** Refuerzo heurístico; **MalAbs sigue evaluando acciones** igual.

---

## 4. Metaplanificación nómada

**Problema:** Metas de días/semanas deben sobrevivir cambio de dispositivo.

**Diseño:** Registro de **metas maestras** (`MetaplanRegistry`) con prioridad; hint opcional al LLM. **Persistencia** junto a checkpoint JSON requiere ampliar `KernelSnapshotV1` (trabajo futuro); el MVP mantiene metas en RAM por sesión.

**Contrato:** Advisory; revocación y UX de consentimiento fuera del núcleo numérico.

---

## Enlaces

| Documento | Rol |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Pipeline; LLM no decide |
| [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | v9 epistémica / generativa / enjambre / metaplan roadmap |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Robustez, privacidad |
| [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) | Persistence, checkpoints |
