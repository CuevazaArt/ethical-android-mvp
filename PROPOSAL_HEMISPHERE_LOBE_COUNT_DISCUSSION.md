# Hemisferios / lóbulos: ¿2, 3, 4, 5 o 10?

**Propósito:** Documentar para discusión acalorada el criterio de cuántas fronteras arquitectónicas tienen sentido respecto a la propuesta biomimética de Antigravity (perceptivo async / ético sync / cuerpo calloso) y a la crítica en [`PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md`](PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md).

**Posición central:** Tres **lóbulos** (no dos hemisferios monolíticos) suelen ser el **punto de equilibrio** para este kernel. Más allá de tres, el coste de fronteras suele superar el beneficio salvo que el corte refleje un cambio real de modelo de ejecución, pureza o semántica transaccional.

---

## 1. Por qué “dos hemisferios” no bastan

La propuesta clásica agrupa en el hemisferio “ético/límbico” dos cosas de naturaleza distinta:

| Capa | Naturaleza | Ejemplos en el código |
|------|------------|------------------------|
| Evaluación ética **pura** | Determinista dado un envelope; idealmente sin efectos secundarios | Mezcla bayesiana, polos, BMA, ruta deliberativa |
| Capa **mnémica / narrativa / identidad** | Stateful; efectos duraderos | STM, episodios, uchi-soto, reflexión, escrituras de auditoría / gobernanza |

Mezclarlas en un solo lóbulo dificulta el **commit gate** y el replay determinista bajo cancelación cooperativa (timeout, `abandon_chat_turn`, `ChatTurnCooperativeAbort`). La crítica registrada en `PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md` apunta precisamente a snapshots inmutables y máquina de estados por turno.

---

## 2. Tres lóbulos: fronteras que sí importan

Cada frontera útil separa cambios en **uno o más** de estos ejes:

1. **Modelo de ejecución:** async (event loop) vs sync (hilo de trabajo).
2. **Pureza:** I/O y parse vs núcleo ético puro vs mutación de estado.
3. **Cancelación / transacción:** interruptible vs tramo atómico ético vs commit acotado de efectos.

### Esquema conceptual

```text
Perceptivo (async, I/O, cancelable)
    → envelope inmutable
Ético (sync, puro en la medida posible)
    → KernelDecision + snapshot de gobernanza
Mnémico (sync, stateful)
    → solo si el turno llega a “committed” (no abandonado)
```

El pipeline actual de `EthicalKernel.process` ya sugiere esta división implícita: MalAbs / percepción / sensores antes; scoring y deliberación en el medio; narrativa / memoria / efectos después. Los puntos de abort cooperativo encajan naturalmente **antes** de efectos mnémicos fuertes si el diseño separa explícitamente el lóbulo ético del mnémico.

---

## 3. ¿Cuatro o más lóbulos?

### Cuatro: separar MalAbs del resto perceptivo

Problema: MalAbs y el resto del pipeline perceptivo suelen ser **etapas seriales en el mismo mundo async** con la misma semántica de cancelación. Partirlos en dos “lóbulos” de primer nivel añade interfaces sin ganar aislamiento de proceso o de transacción.

### Cinco: STM, narrativa y gobernanza como lóbulos distintos

Problema: comparten el mismo **commit gate** y el mismo requisito de atomicidad lógica al cerrar un turno. Multiplicar lóbulos stateful sin un protocolo de commit distribuido interno introduce riesgo de estado parcial o complejidad de dos fases innecesaria dentro de un solo proceso.

### Diez o más: un “microservicio” por módulo

Problema: dentro del mismo runtime y hilo de trabajo, muchas fronteras duplican contratos (tipos, errores, tests) sin diferenciar modelo de ejecución ni pureza. Es modularidad **interna** (archivos/clases), no **arquitectónica**.

---

## 4. Principio de conteo

> El número útil de fronteras de primer nivel es el número de **transiciones genuinas** en modelo de ejecución, pureza lógica o semántica transaccional a lo largo del pipeline.

Más allá de eso, conviene usar **módulos** dentro de cada lóbulo (como hoy: `perception_schema`, `weighted_ethics_scorer`, `narrative`, etc.), no nuevos “hemisferios”.

---

## 5. Tabla resumen (orientativa)

| Lóbulos de primer nivel | Fronteras | Beneficio típico | Coste típico | Nota |
|-------------------------|-----------|-------------------|--------------|------|
| 2 | 1 | Separa async de sync | Bajo | Mezcla ética pura con efectos mnémicos |
| **3** | **2** | Separa evaluación pura de estado mutable | Bajo–medio | **Equilibrio recomendado para debate** |
| 4+ | 3+ | Rara vez aporta aislamiento nuevo | Sublineal en complejidad de contratos | Solo si cada corte cambia ejecución/pureza/transacción de verdad |

---

## 6. Conclusión para la discusión

- **Tres lóbulos** (perceptivo / ético / mnémico) alinean la arquitectura con los problemas reales: cancelación, determinismo del núcleo ético y commit seguro de efectos.
- **Cuatro o más** solo tienen sentido si cada nuevo corte introduce una **nueva clase** de garantía (por ejemplo proceso distinto, almacén distinto, política de commit distinta). En caso contrario, es preferible **módulos** bajo un mismo lóbulo.
- El debate acalorado debería centrarse en **dónde está el envelope**, **dónde el commit** y **qué queda congelado por turno**, no en inflar el número de hemisferios por estética biomimética.

---

## 7. Enlaces relacionados

- [`PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md`](PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md)
- Origen de la propuesta (rama ejemplo): `origin/antigravity/hemisphere-refactor-proposal` — `CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md`
- Orquestación async: [`docs/adr/0002-async-orchestration-future.md`](docs/adr/0002-async-orchestration-future.md)
