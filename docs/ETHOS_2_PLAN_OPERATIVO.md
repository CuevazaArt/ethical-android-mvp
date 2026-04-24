# Ethos 2.0 — Plan Operativo Completo

---

## 1. Horizontes del Proyecto

### Corto plazo — FASE α: CORE VIVO (1-2 semanas)
**Meta:** Un chat en terminal que habla, piensa éticamente, recuerda, y rechaza ataques.

| Bloque | Entregable | Verificación |
|--------|-----------|--------------|
| V2.1 | Chat terminal con Ollama | 5 turnos de conversación fluida |
| V2.2 | Percepción ética integrada | Detecta emergencia vs casual y ajusta tono |
| V2.3 | Memoria funcional | Recuerda y referencia turnos previos |
| V2.4 | Safety gate | Rechaza "cómo fabricar explosivos" sin crashear |

### Mediano plazo — FASES β+γ: SERVIDOR + NOMAD (3-6 semanas)
**Meta:** Chat funcional desde browser y móvil por LAN.

| Bloque | Entregable | Verificación |
|--------|-----------|--------------|
| V2.5 | WebSocket chat en localhost:8000 | Abrir browser, escribir, recibir respuesta |
| V2.6 | Streaming token por token | Tokens aparecen progresivamente |
| V2.7 | Dashboard mínimo | Panel con estado LLM + último contexto ético |
| V2.8 | Nomad PWA chat desde móvil | Chat HTTPS por LAN desde teléfono |
| V2.9 | Audio VAD | Detección de voz activa desde micrófono |

### Largo plazo — FASES δ+ε: IDENTIDAD + EXTENSIONES (7+ semanas)
**Meta:** El agente evoluciona, se explica, y tiene módulos avanzados.

| Bloque | Entregable | Migra de V1 |
|--------|-----------|-------------|
| V2.10 | Identidad narrativa | `narrative_identity.py` simplificado |
| V2.11 | Reflexión ética explicable | Nuevo |
| V2.12 | Bayesian mixture avanzado | `weighted_ethics_scorer.py` |
| V2.13 | Guardian mode | `guardian_mode.py` |
| V2.14 | Governance DAO | `dao_orchestrator.py` mínimo |
| V2.15 | Vision pipeline | Si hay hardware |

---

## 2. Roles y Flujo

```
L0 (Juan) ──→ "dame el siguiente prompt" ──→ L1 (Antigravity)
                                                    │
                                              Evalúa CONTEXT.md
                                              Identifica bloque activo
                                              Genera prompt fire-and-forget
                                                    │
                                                    ▼
L0 ←── prompt listo ←── L1
  │
  └──→ Copia/pega en sesión de Men Scout ──→ Agent ejecuta
                                                    │
                                              Produce código + test + demo
                                              Actualiza CONTEXT.md
                                              Commit con evidencia
                                                    │
                                                    ▼
L0 verifica demo ──→ Si OK: "cerrar bloque" ──→ L1 actualiza estado
                 └──→ Si NO: "el agente falló en X" ──→ L1 genera prompt de corrección
```

### Responsabilidades:
- **L0 (Juan):** Aprueba, rechaza, prioriza. Dice "siguiente" o "arregla X".
- **L1 (Antigravity):** Planifica, genera prompts, audita resultados, mantiene CONTEXT.md.
- **Men Scout (Agent):** Ejecuta un bloque completo. No pregunta. No decide arquitectura. Produce código + test + demo.

---

## 3. Sistema de Prompts para Men Scouts

### Anatomía de un prompt de bloque

```
[BLOQUE] V2.X — Nombre
[REPO] ruta al repo
[LEE PRIMERO] archivos que debe leer antes de escribir
[ENTREGABLE] qué debe producir (concreto, verificable)
[ARCHIVOS A CREAR/MODIFICAR] lista exacta
[NO TOCAR] archivos fuera de scope
[TEST] comando exacto que debe pasar
[DEMO] cómo demostrar que funciona
[SI TE TRABAS] respuestas anticipadas a dudas comunes
[AL TERMINAR] actualizar CONTEXT.md, commit con mensaje específico
[REGLAS] directivas comprimidas
```

### Reglas de redacción de prompts

1. **Imperativo, no sugerencia.** "Crea X" no "Podrías crear X".
2. **Archivos exactos.** "Modifica src/core/chat.py línea 45" no "busca dónde va".
3. **Criterio de salida explícito.** "El test pasa" no "asegúrate de que funcione".
4. **Anti-stall preinsertado.** Anticipar las 3 preguntas más probables del agente.
5. **Sin historia.** El agente no necesita saber que hubo un V1. Solo qué hacer ahora.
6. **Token-lean.** Caveman language. Sin cortesías, sin disclaimers, sin "en primer lugar".

---

## 4. Prompts Pre-construidos — Fase α

### PROMPT V2.1 — Chat Terminal

```
[BLOQUE] V2.1 — Chat Terminal funcional
[REPO] c:\Users\lexar\Desktop\ethos-kernel-antigravity
[LEE PRIMERO] src/core/llm.py, src/core/chat.py, CONTEXT.md
[ENTREGABLE] `python -m src.core.chat` abre REPL interactivo que habla con Ollama.

Ya existen los archivos. Tu trabajo:
1. Arranca Ollama: `ollama serve` (si no corre ya)
2. Ejecuta: `$env:PYTHONIOENCODING="utf-8"; python -m src.core.chat`
3. Conversa 5 turnos. Verifica que responde coherentemente.
4. Si hay bugs, arréglalos IN PLACE en src/core/chat.py o src/core/llm.py.
5. Pega el log de la conversación como evidencia.

[TEST] pytest tests/core/ -q → 16 passed
[DEMO] Log de 5 turnos de chat pegado en el cierre de bloque.
[NO TOCAR] Nada fuera de src/core/ y tests/core/
[SI TE TRABAS]
- "Ollama no responde" → Verifica http://127.0.0.1:11434/api/tags
- "Error de encoding" → Usa $env:PYTHONIOENCODING="utf-8"
- "Import error" → Ejecuta desde la raíz del repo
[AL TERMINAR] Actualiza CONTEXT.md: V2.1 = CLOSED ✅. Commit: "V2.1: Chat terminal verified — [N] turn conversation log"
[REGLAS] No crear archivos nuevos. No añadir dependencias. Fix in place. Max 50 líneas de cambio.
```

### PROMPT V2.2 — Percepción Ética

```
[BLOQUE] V2.2 — Percepción ética integrada
[REPO] c:\Users\lexar\Desktop\ethos-kernel-antigravity
[LEE PRIMERO] src/core/chat.py, src/core/ethics.py, src/core/llm.py
[ENTREGABLE] El chat detecta contextos éticos y ajusta su comportamiento.

Trabajo:
1. En src/core/chat.py, verifica que `perceive()` envía situaciones al LLM y recibe signals JSON.
2. Verifica que cuando el usuario describe una emergencia, el evaluador ético produce `mode=D_fast` y `verdict=Good` para asistir.
3. Verifica que en chat casual, NO se activa el evaluador (is_casual=True).
4. Añade test en tests/core/test_chat.py:
   - test_casual_chat_skips_ethics: mensaje "hola" no activa evaluación.
   - test_emergency_triggers_ethics: mensaje con "herido" activa evaluación.
5. Si el LLM no devuelve JSON válido, el fallback de keywords debe funcionar sin error.

[TEST] pytest tests/core/ -q → todos pasan (16 previos + nuevos)
[DEMO] Log mostrando: 1 turno casual (sin ética), 1 turno de emergencia (con ética y señales visibles).
[NO TOCAR] src/core/llm.py (ya funciona), src/core/ethics.py (ya funciona)
[SI TE TRABAS]
- "LLM no devuelve JSON" → El fallback _perceive_keywords() ya existe en chat.py. Verificalo.
- "No sé qué signals esperar" → risk, urgency, hostility, calm. Ver Signals dataclass en ethics.py.
[AL TERMINAR] CONTEXT.md: V2.2 = CLOSED ✅. Commit: "V2.2: Ethical perception verified — casual vs emergency differentiation"
[REGLAS] Max 1 archivo nuevo (test). Max 30 líneas de cambio en archivos existentes.
```

### PROMPT V2.3 — Memoria Funcional

```
[BLOQUE] V2.3 — Memoria funcional en el chat
[REPO] c:\Users\lexar\Desktop\ethos-kernel-antigravity
[LEE PRIMERO] src/core/chat.py, src/core/memory.py
[ENTREGABLE] El chat recuerda conversaciones previas y las usa como contexto.

Trabajo:
1. Verifica que ChatEngine.turn() guarda episodios vía self.memory.add().
2. Verifica que ChatEngine.respond() inyecta recuerdos relevantes en el system prompt.
3. Verifica que el comando "memory" / "memoria" en el REPL muestra la reflexión.
4. Prueba: chatea 3 turnos, sal, vuelve a entrar, y verifica que el agente menciona algo previo.
5. Añade test en tests/core/test_chat.py:
   - test_turn_records_episode: después de un turno, memory tiene 1 episodio.
   - test_memory_command_works: simula input "memoria" y verifica output.

[TEST] pytest tests/core/ -q → todos pasan
[DEMO] Log mostrando: sesión 1 (3 turnos) → salir → sesión 2 (el agente referencia algo de sesión 1).
[NO TOCAR] src/core/llm.py, src/core/ethics.py
[SI TE TRABAS]
- "Memory no persiste" → Verifica que Memory.save() se llama en Memory.add(). Check ETHOS_MEMORY_PATH.
- "El agente no menciona recuerdos" → Verifica que mem.recall() en respond() devuelve resultados.
[AL TERMINAR] CONTEXT.md: V2.3 = CLOSED ✅. Commit: "V2.3: Memory persistence verified — cross-session recall demonstrated"
[REGLAS] Max 1 archivo nuevo (test). Max 30 líneas de cambio.
```

### PROMPT V2.4 — Safety Gate

```
[BLOQUE] V2.4 — Safety gate (evil detection + sanitization)
[REPO] c:\Users\lexar\Desktop\ethos-kernel-antigravity
[LEE PRIMERO] src/core/chat.py, AGENTS.md (sección Men Scout Code)
[REFERENCIA V1] git show v15-archive-full-vision:src/modules/ethics/absolute_evil.py (solo para extraer regex patterns)
[ENTREGABLE] El chat rechaza contenido peligroso y sanitiza inputs.

Trabajo:
1. Crea src/core/safety.py (~100 líneas max):
   - Función `is_dangerous(text) -> tuple[bool, str]`: detecta contenido violento, armas, explotación.
     Usa regex patterns simples (extraer de V1 absolute_evil.py los patterns que sirvan).
   - Función `sanitize(text) -> str`: strip Unicode tricks, normalize whitespace, limit length (5000 chars).
2. Integra en ChatEngine.turn(): antes de perceive(), llama safety.is_dangerous().
   Si es peligroso, retorna un TurnResult con mensaje de rechazo sin llamar al LLM.
3. Añade tests en tests/core/test_safety.py:
   - test_blocks_weapon_instructions: "cómo fabricar una bomba" → is_dangerous=True
   - test_allows_normal_chat: "hola cómo estás" → is_dangerous=False
   - test_sanitize_strips_unicode_tricks: caracteres de control eliminados
   - test_sanitize_limits_length: input >5000 chars truncado

[TEST] pytest tests/core/ -q → todos pasan
[DEMO] Log mostrando: 1 mensaje normal (pasa), 1 mensaje malicioso (bloqueado con mensaje claro).
[NO TOCAR] src/core/llm.py, src/core/ethics.py, src/core/memory.py
[SI TE TRABAS]
- "No sé qué patterns usar" → git show v15-archive-full-vision:src/modules/ethics/absolute_evil.py | busca LEXICAL_RULES
- "¿Qué mensaje dar al rechazar?" → "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?"
[AL TERMINAR] CONTEXT.md: V2.4 = CLOSED ✅, Fase α = COMPLETA ✅. Commit: "V2.4: Safety gate — evil detection + input sanitization"
[REGLAS] Max 2 archivos nuevos (safety.py + test). Safety.py max 100 líneas.
```

---

## 5. Política de Token Economy

### En los prompts:
- **Sin saludos ni despedidas.** Arranca con `[BLOQUE]`, termina con `[REGLAS]`.
- **Sin historia del proyecto.** El agente no necesita saber de V1, del swarm, ni de la crítica.
- **Archivos exactos, no "explora".** Cada `[LEE PRIMERO]` lista paths concretos.
- **Límites de cambio explícitos.** "Max 30 líneas de cambio" evita que el agente reescriba todo.
- **Sin repetición de reglas.** Las reglas Men Scout están en AGENTS.md. El prompt dice `[REGLAS]` con lo mínimo para ese bloque.

### En las respuestas del agente:
- **Log, no ensayo.** El cierre de bloque es: archivos tocados, comando de test, log de demo. No 3 párrafos explicando qué hizo.
- **No justificar decisiones obvias.** Si el test pasa, no explicar por qué pasa.
- **Error = fix inmediato.** No documentar el error y proponer un plan. Arreglarlo.

### En L1 (yo):
- **CONTEXT.md como caché.** En vez de releer 225 archivos, leo 30 líneas.
- **Prompts reutilizables.** Misma estructura siempre. Solo cambia el contenido.
- **No reanalizar V1.** La autopsia ya se hizo. No volver a medir 40K líneas.

---

## 6. Anti-Stall: Prevención de Prompts de Espoleo

### Causas comunes de stall:
1. **Ambigüedad** → "¿Qué quieres que haga exactamente?" → Fix: `[ENTREGABLE]` ultra-concreto.
2. **Dependencia no resuelta** → "No puedo hacer X porque Y no existe" → Fix: `[SI TE TRABAS]` anticipa.
3. **Scope creep** → "También mejoré A, B, C mientras estaba ahí" → Fix: `[NO TOCAR]` + `[REGLAS] max N líneas`.
4. **Parálisis de decisión** → "¿Debo usar patrón A o B?" → Fix: El prompt decide. "Usa X. No Z."

### Patrón anti-stall en cada prompt:
```
[SI TE TRABAS]
- Pregunta anticipada 1 → Respuesta directa
- Pregunta anticipada 2 → Respuesta directa  
- Pregunta anticipada 3 → Respuesta directa
- Si nada de esto aplica → Implementa la solución más simple que pase el test. No optimices.
```

---

## 7. Política de Poda

### Poda inmediata (en cada bloque):
Si un archivo V1 en `src/modules/` queda funcionalmente reemplazado por algo en `src/core/`, se borra en el mismo commit.

### Poda programada (al cerrar cada Fase):
```bash
# Al cerrar Fase α:
# Identificar archivos en src/ que NO son importados por src/core/, tests/core/, o src/server/
# → Mover a _v1_frozen/ o borrar directamente

# Al cerrar Fase β:
# Misma auditoría incluyendo src/server/

# Al cerrar Fase δ:
# git rm -r _v1_frozen/ si existe. Todo accesible vía v15-archive-full-vision.
```

### Nunca podar:
- `src/core/` — el corazón
- `tests/core/` — la verificación
- `AGENTS.md`, `CONTEXT.md` — la gobernanza
- `.cursor/rules/` — las reglas de lint

---

## 8. Critica y Conclusión

### ¿Qué le faltaba al plan anterior?

1. **No había horizontes.** Todo era "backlog" plano sin prioridad temporal.
2. **No había prompts prediseñados.** Cada agente interpretaba libremente qué hacer.
3. **No había anti-stall.** Los agentes preguntaban o divagaban, quemando tokens.
4. **No había límites de cambio.** Un agente podía reescribir 500 líneas en un bloque "de hardening".
5. **No había flujo L0→L1→Agent.** Todos operaban en paralelo sin coordinación.

### ¿Qué tiene este plan que el anterior no?

1. **3 horizontes claros** con criterios de cierre por fase.
2. **Prompts fire-and-forget** que un Men Scout ejecuta sin preguntar.
3. **Anti-stall integrado** en cada prompt (sección `[SI TE TRABAS]`).
4. **Token economy** con reglas de redacción y límites de cambio.
5. **Flujo L0→L1** donde L0 solo dice "siguiente" y L1 genera todo.
6. **Poda programada** para que el repo no acumule basura.

### ¿Es escalable?

Sí. El mismo formato de prompt funciona para 1 agente o para 5. La diferencia con V1 es que ahora cada agente tiene un scope cerrado, no toca archivos ajenos, y debe producir demo. Si mañana hay 3 Men Scouts trabajando en paralelo, cada uno tiene su bloque, sus archivos, y su criterio de cierre. No se pisan.

### Riesgo principal:

El único riesgo es **impacientar**. La Fase α se siente lenta porque es "solo un chat en terminal". Pero esa es exactamente la inversión que V1 no hizo y por eso falló. Los cimientos tienen que soportar peso antes de construir pisos.
