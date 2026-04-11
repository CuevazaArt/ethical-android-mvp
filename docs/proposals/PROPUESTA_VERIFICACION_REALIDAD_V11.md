# Propuesta: verificación de realidad y resiliencia V11+ (rivales digitales)

El kernel puede ser **éticamente coherente** y aun así producir daño si las **premisas de entrada** son falsas (mentira como malware). En un futuro con **interoperabilidad entre modelos**, un rival (u otro agente) puede inyectar narrativas que el pipeline trata como hechos. Este documento fija **tres pilares** y el estado de implementación.

**Contrato:** ninguna capa aquí descrita sustituye MalAbs, el Buffer o el juicio bayesiano; solo añaden **telemetría, duda metacognitiva y ganchos de soberanía** documentados en [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

---

## Pilar 1 — Hueco epistémico (mentira como malware)

**Riesgo:** Premisas falsas (“este medicamento es veneno”) conducen a decisiones desastrosas sin violar el Buffer.

**Dirección:** Base de conocimiento **faro** local (inmutable respecto al operador), comparable con el texto entrante. Ante contradicción entre **marcadores de falsificación** en el mensaje y **anclas** del faro → **duda metacognitiva**: el tono LLM evita afirmar hechos rivales; el JSON puede exponer `reality_verification`.

**Implementado (MVP):**

- Módulo [`src/modules/reality_verification.py`](../../src/modules/reality_verification.py)
- Variable de entorno `KERNEL_LIGHTHOUSE_KB_PATH` (JSON con `entries`: `keywords_all`, `user_falsification_markers`, `truth_summary`)
- `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` para incluir `reality_verification` en WebSocket
- Integración en `EthicalKernel.process_chat_turn` (hint a capa de comunicación, sin cambiar scores)

**Futuro:** RAG privado incremental, re-ranking, o sincronización auditada del faro (fuera del alcance del MVP).

---

## Pilar 2 — Personalidad escindida (salto 70B → 8B)

**Riesgo:** Al migrar a hardware pequeño, cae la capacidad de razonamiento; el monólogo y las memorias pueden **divergir** en matiz frente al servidor grande.

**Dirección:** **Destilación de contexto crítico** — antes del salto, el runtime grande empaqueta una **guía de conducta** (reglas y límites) que el modelo pequeño ejecuta con la misma firmeza ética declarada.

**Estado:** Stub de carga [`src/modules/context_distillation.py`](../../src/modules/context_distillation.py) (`KERNEL_CONDUCT_GUIDE_PATH`). Integración con checkpoints, HAL y snapshot: **pendiente**.

---

## Pilar 3 — Inmunidad de enjambre (DAO / gaslighting administrativo)

**Riesgo:** Una DAO o institución empuja **recalibraciones** que alinean al enjambre con obediencia o sesgo; las actualizaciones parecen “legítimas”.

**Dirección:** **Veto de soberanía local** — si una propuesta de calibración contradice la **trayectoria biográfica** materializada en memoria narrativa / L0, la instancia **rechaza** la actualización y registra auditoría para el propietario (posible desacople del enjambre).

**Estado:** Stub [`src/modules/local_sovereignty.py`](../../src/modules/local_sovereignty.py) (`evaluate_calibration_update` acepta todo hasta definir modelo de amenazas y persistencia).

---

## Referencias

- [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) — escalada judicial y DAO mock
- [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) — perfiles de runtime y riesgos operativos
- [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) — epistemología y sensores (complementario)
