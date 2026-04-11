# Ollama vs Hugging Face — rol en Ethos Kernel

Documento de **síntesis de equipo** + alineación con el código. No sustituye [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) ni [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md).

---

## Cuadro comparativo (resumen)

| Característica | Hugging Face | Ollama |
|----------------|--------------|--------|
| Naturaleza | Plataforma + ecosistema (p. ej. `transformers`, modelos en Hub) | Runtime local con API HTTP (`localhost:11434` típico) |
| Tipos de IA | Muy amplio (texto, visión, audio, embeddings, etc.) | Principalmente LLMs (texto) y algunos modelos multimodales vía Ollama |
| Memoria / hardware | Modelos “completos” suelen ser pesados (GPU útil según modelo) | Modelos **cuantizados** (p. ej. GGUF), razonables en PC/Mac sin datacenter |
| Integración típica | Código Python (`transformers`, `sentence-transformers`, etc.) | Cliente HTTP: ya integrado en este repo vía `OllamaCompletion` |

---

## Cómo se aplica al Ethos Kernel (dos capas distintas)

### A) Ollama — capa de **lenguaje** (ya soportada)

**Rol:** traducir texto ↔ señales (`LLMModule.perceive`), generar respuesta verbal, narrativa rica, monólogo opcional — **sin** decidir la acción ética final (el kernel sí).

**En código:** `src/modules/llm_backends.py` (`OllamaCompletion`), resolución de modo con `LLM_MODE=ollama` / `USE_LOCAL_LLM`. Ver README sección LLM / chat.

**Por qué encaja:** ejecución **local**, sin API de pago obligatoria, útil para demos y privacidad.

### B) Hugging Face / embeddings — **refuerzo opcional del gate de chat** (diseño futuro)

**Rol propuesto (no sustituto del núcleo):** complementar las **listas de frases** en `AbsoluteEvilDetector.evaluate_chat_text` con una señal de **similitud semántica** frente a frases de referencia (p. ej. categorías de riesgo), en **milisegundos** y sin generar texto largo.

**En código hoy:** MalAbs chat sigue siendo **substring + normalización** (`input_trust.normalize_text_for_malabs`). Ver [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) — paráfrasis y lenguaje indirecto siguen siendo riesgo residual.

**Por qué HF encaja conceptualmente:** modelos pequeños de **embeddings** vía `sentence-transformers` (u otro stack ligero) son adecuados para **clasificación por similitud**, no para “pensar” la ética del episodio (eso sigue siendo kernel + MalAbs estructural en acciones).

**Límites explícitos:**

- No reemplaza el veto MalAbs sobre **acciones** (`CandidateAction` + señales).
- No es “moderación infalible”: umbrales, sesgos del modelo de embedding y ataques adaptativos requieren tests y gobernanza (ver [ADR 0003](adr/0003-optional-semantic-chat-gate.md)).

---

## Valor implementable ya vs siguiente PR

| Entregable | Estado |
|------------|--------|
| Ollama como backend de percepción/comunicación | **Implementado** — activar con variables de entorno documentadas en README |
| Puente de código para gate semántico opcional | **Implementado (Ollama embeddings)** — `src/modules/semantic_chat_gate.py`; activar con `KERNEL_SEMANTIC_CHAT_GATE=1` |
| Dependencias HF (`sentence-transformers`, etc.) | **No** en CI — se usa la API HTTP de Ollama (`/api/embeddings`), misma base que el LLM |
| Integración en `evaluate_chat_text` | **Hecha** — cadena embedding → substring; umbrales vía `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` |

---

## Enlaces

- [ADR 0003 — Semantic chat gate (optional, future)](adr/0003-optional-semantic-chat-gate.md)  
- `src/modules/llm_backends.py`, `src/modules/llm_layer.py`  
- `src/modules/absolute_evil.py` — `evaluate_chat_text`  
- [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) (contexto v9)
