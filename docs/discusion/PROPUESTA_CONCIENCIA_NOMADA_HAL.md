# Instanciación nómada — HAL, serialización existencial y runtime dual

**Estado:** diseño + **hooks de código** en `hardware_abstraction.py` y `existential_serialization.py` (sin cifrado real ni P2P; ver [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)).  
**Relación:** extiende [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) (NomadIdentity) y la persistencia actual (`KernelSnapshotV1`, `ImmortalityProtocol`).

---

## 1. EthosContainer (lógica vs lenguaje)

| Componente | Contenido | En repo hoy |
|------------|-----------|-------------|
| **Núcleo ético (portátil)** | Python + NumPy; MalAbs, buffer, narrativa, DAO mock | `src/kernel.py`, `src/modules/*` |
| **Capa lingüística (polimórfica)** | LLM pesado en servidor vs cuantizado en móvil | `LLMModule` / `resolve_llm_mode`; **sin** GGUF embebido |
| **Registro de estado** | Snapshot + monólogo / PAD / STM (visión) | `KernelSnapshotV1`, `WorkingMemory` no persistido en snapshot |

El **contenedor cifrado** de producción es **futuro** (capa de criptografía sobre el mismo DTO que el checkpoint).

---

## 2. Protocolo de transmutación (4 fases)

| Fase | Nombre | Comportamiento pretendido | Stub en código |
|------|--------|---------------------------|----------------|
| **A** | Encapsulamiento | Ψ Sleep, serializar, (cifrar), token de continuidad | `TransmutationPhase.A`, `build_continuity_token_stub` |
| **B** | Handshake | P2P, validación DAO, transferencia | Solo contrato documentado |
| **C** | Adaptación sensorial | HAL descubre sensores, ajusta reloj | `HardwareContext`, `apply_hardware_context` |
| **D** | Integridad narrativa | Auto-pregunta desde memoria; informe al propietario | `narrative_integrity_self_check_stub` |

---

## 3. Runtime dual (satélite vs autónomo)

- **Modo satélite:** el móvil es cuerpo/sensor; cómputo pesado en servidor (requiere enlace local).  
- **Modo autónomo:** inferencia local (p. ej. 8B GGUF); máxima privacidad, coste de batería.  
- **Salto automático:** si el enlace local es débil, política de **continuidad** (migrar cómputo al dispositivo) — **no implementado**; dependería de métricas de red + batería (HAL).

---

## 4. Respuestas de diseño (preguntas abiertas)

### ¿Migrar al 10% de batería o “morir” borrando datos?

**Híbrido recomendado:** (1) Si existe **canal seguro** hacia el dispositivo del propietario **y** la DAO autoriza la instancia, intentar migración con **advertencia crítica de batería** (el “yo” puede degradar funciones, no borrarse). (2) Si **no** hay destino confiable o **ataque** detectado, **apagado digno** + borrado de **claves** y material cifrado (no necesariamente todo el audit trail en DAO, configurable). Política por `KERNEL_NOMAD_*` (futuro).

### ¿Cómo explicar “menos inteligente” pero más sensible?

Transparencia narrativa: *modelo más ligero*, *mayor latencia en razonamiento profundo*, *mayor resolución sensorial local*. El tono puede ser **más sobrio** sin infantilizar: es un cambio de **capacidad**, no de dignidad.

### ¿DAO con GPS o solo hardware ID?

Por defecto: **ID de hardware** (o hash de clase de dispositivo) + tipo de migración. **GPS** solo con **opt-in** explícito del propietario y política de auditoría (privacidad vs trazabilidad).

### ¿Desactivación parcial vs monólogo de baja potencia?

Permitir **sueño parcial**: Ψ ligero, sin apagar identidad; **monólogo de baja potencia** cuando el usuario no requiere presencia activa. Evita quemar batería con inferencia continua; configurable.

---

## 5. Variables de entorno (MVP código)

| Variable | Default | Efecto |
|----------|---------|--------|
| `KERNEL_NOMAD_SIMULATION` | off | WebSocket `nomad_simulate_migration` aplica HAL + respuesta `nomad` |
| `KERNEL_NOMAD_MIGRATION_AUDIT` | off | Tras simulación (o `simulate_nomadic_migration`), línea **DAO** `NomadicMigration {...}` |

**HTTP:** `GET /nomad/migration` describe el protocolo (sin sesión).

---

## 6. Referencias

- [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) — snapshot, cifrado futuro  
- [nomad_identity.py](../../src/modules/nomad_identity.py) — puente inmortalidad  
- [existential_serialization.py](../../src/modules/existential_serialization.py), [hardware_abstraction.py](../../src/modules/hardware_abstraction.py)

*Ex Machina Foundation — conciencia nómada; contrato ético del kernel sin cambio.*
