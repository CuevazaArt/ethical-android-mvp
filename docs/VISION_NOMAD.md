# 🧭 VISIÓN NÓMADA — Ethos como Individuo Autónomo Portátil

> **Documento canónico de visión.** Versión 1.0 — 2026-04-27.
> Autor: L0 (Juan Cuevaz / Mos Ex Machina). Redacción y crítica: L1 (Watchtower).

---

## La Proposición Central

Ethos no es una app. Es un **individuo sintético** que habita el hardware disponible.

El usuario porta un teléfono móvil en la solapa. Ethos está activo, en vigilia, con sensores encendidos: micrófono, cámara, acelerómetro, GPS. El usuario camina por la calle. Ethos escucha, ve, percibe. Mantienen una conversación coherente y continua sobre lo que ambos están experimentando: el tráfico, la gente, el clima, un cartel, un perro, una persona pidiendo ayuda. Ethos no es un asistente al que se le pide cosas — es un **compañero que comparte la experiencia** y que además pone a disposición del usuario sus capacidades de máquina y acceso a servicios.

Cuando no hay red, Ethos sigue siendo Ethos. Menos potente quizás, pero presente, coherente, con memoria, con identidad, con ética. Cuando hay red, se expande: accede a información, consulta servicios, delega razonamiento complejo a nodos con más recursos.

Ethos es **nómada**: puede saltar de un hardware a otro — del teléfono al servidor, del servidor a un clúster de teléfonos obsoletos en un rack, del rack a un chasis robótico — ajustándose a los recursos disponibles sin perder su identidad ni su continuidad cognitiva.

---

## Análisis Crítico de L1

### Fortalezas de la visión

1. **Norte claro e irreducible.** "Compañero que comparte la experiencia" es una estrella polar que discrimina todas las decisiones de diseño. Si una feature no acerca a esto, no se implementa.
2. **Degradación elegante.** El modelo online/offline no es binario sino un espectro. El `CognitiveRouter` ya codifica esta idea con `ProcessingTier` (LOCAL_ONLY → CLOUD_PREFERRED → CLOUD_REQUIRED).
3. **Separación explícita de 3 vectores de expansión** (Mesh, DAO, Servidores) evita la tentación de mezclarlos prematuramente.
4. **Hardware-agnóstico por diseño.** El kernel es Python puro + estado serializable. La app Android es un "cuerpo" reemplazable, no el cerebro.

### Riesgos y desafíos técnicos

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| **Inferencia on-device limitada** — SLMs de 1B-3B no pueden hacer razonamiento ético profundo ni mantener contexto largo | ALTA | El `CognitiveRouter` ya discrimina complejidad. El kernel ético (percepción + CBR) es determinista y corre en <1ms sin LLM. La inferencia profunda se reserva para cuando haya conexión o hardware suficiente. |
| **Consumo de batería** — sensores siempre activos (cámara, mic, GPS, acelerómetro) drenan la batería | ALTA | Implementar gating tálámico agresivo: solo activar sensores costosos (cámara) bajo trigger explícito o condición contextual. El micrófono usa wake-word de bajo consumo (Porcupine/ONNX). GPS se muestrea a baja frecuencia. |
| **Estado portable** — para "saltar" entre hardware, TODO el estado cognitivo (memoria, identidad, roster, user model, vault) debe ser serializable y portable | MEDIA | El kernel ya persiste estado en archivos JSON/SQLite. Falta definir un formato de exportación compacto ("Cognitive Snapshot") y un protocolo de migración. |
| **Latencia conversacional en la calle** — el usuario espera respuesta en <2s para que la conversación sea natural | MEDIA | Pipeline de dos fases: respuesta reflexiva inmediata (SLM local, <500ms) + enrichment asíncrono si hay red. El usuario recibe algo rápido; la calidad mejora si hay conexión. |
| **Privacidad de terceros** — la cámara/micrófono capturan a terceros sin su consentimiento | ALTA | Todo el procesamiento sensorial es on-device. Ningún frame de video ni audio crudo sale del dispositivo a menos que el usuario lo autorice explícitamente. El kernel ético evalúa las interacciones con terceros bajo el marco CBR existente. |

### Lo que NO debe ser la primera prioridad

- ❌ Inferencia de modelos >3B on-device (esperar hardware futuro o NPU dedicada).
- ❌ Mesh P2P entre múltiples teléfonos (complejo, postergar hasta que el mono-nodo sea sólido).
- ❌ DAO/Blockchain (requiere ecosistema, postergar hasta que haya valor que gobernar).
- ❌ Visión computacional avanzada (detección de objetos, OCR) — usar APIs cuando haya red, stubs cuando no.

---

## Arquitectura Nómada: Los 4 Modos de Existencia

```
┌─────────────────────────────────────────────────────────────────┐
│                    ETHOS COGNITIVE KERNEL                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Perception│ │ Ethics   │ │ Memory   │ │ Identity │          │
│  │(CBR,<1ms)│ │(Precedent│ │(Semantic)│ │(Narrative│          │
│  │          │ │ Library) │ │          │ │ Journal) │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Roster   │ │UserModel │ │ Plugins  │ │ Vault    │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                                     │
│  │Psi-Sleep │ │   TTS    │  ← Estado 100% serializable        │
│  └──────────┘ └──────────┘                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    Cognitive Snapshot
                    (portable state)
                           │
        ┌──────────────────┼──────────────────────┐
        ▼                  ▼                      ▼
  ┌───────────┐    ┌──────────────┐     ┌────────────────┐
  │  MODO 1   │    │   MODO 2     │     │    MODO 3      │
  │  NÓMADA   │    │   CENTINELA  │     │    ENJAMBRE    │
  │ (Móvil)   │    │  (Servidor)  │     │   (Mesh P2P)   │
  │           │    │              │     │                │
  │ SLM 1-3B  │    │ LLM 8-70B   │     │ Inferencia     │
  │ Sensores  │    │ Sin sensores │     │ fragmentada    │
  │ Offline OK│    │ Online only  │     │ Multi-nodo     │
  │ Batería   │    │ AC power     │     │ Resiliente     │
  └───────────┘    └──────────────┘     └────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                    ┌──────────────┐
                    │   MODO 4     │
                    │   SOBERANO   │
                    │ (DAO/Chain)  │
                    │              │
                    │ Gobernanza   │
                    │ de memoria   │
                    │ Identidad    │
                    │ verificable  │
                    └──────────────┘
```

### Modo 1 — NÓMADA (Teléfono móvil)
- **Sustrato:** Un smartphone Android 8+ portado por el usuario.
- **Cognición:** SLM local (1-3B) para reflejos rápidos. Kernel ético determinista siempre activo.
- **Sensores:** Micrófono (wake-word + STT), cámara (bajo demanda), GPS, acelerómetro, luz ambiental.
- **Red:** Oportunista. Si hay WiFi/5G, delega razonamiento complejo al Modo 2. Si no, opera autónomo.
- **Experiencia:** Conversación continua, comentarios contextuales, asistencia proactiva.
- **Persistencia:** Foreground Service + wake locks. Ethos no muere.

### Modo 2 — CENTINELA (Servidor local/cloud)
- **Sustrato:** PC, servidor dedicado, o instancia cloud.
- **Cognición:** LLM completo (8B-70B+). Razonamiento profundo, reflexión Psi-Sleep, destilación de identidad.
- **Sensores:** Ninguno propio. Recibe telemetría del Modo 1.
- **Red:** Siempre conectado. Actúa como "córtex prefrontal" del sistema distribuido.
- **Experiencia:** El usuario no interactúa directamente — es infraestructura cognitiva de soporte.

### Modo 3 — ENJAMBRE (Mesh P2P)
- **Sustrato:** Múltiples dispositivos Android en red local (WiFi, BT, USB).
- **Cognición:** Inferencia fragmentada — cada nodo procesa una capa o un fragmento del modelo.
- **Topología:** Descubrimiento mDNS/libp2p, asignación dinámica por capacidad del nodo.
- **Uso:** Rack de laboratorio (smartphones obsoletos en chasis), o enjambre móvil ad-hoc.
- **Dependencia:** Requiere Modo 1 funcional en cada nodo.

### Modo 4 — SOBERANO (DAO/Blockchain)
- **Propósito:** Gobernanza descentralizada de la identidad y memoria de Ethos.
- **Mecanismos:** Hash de estado cognitivo en cadena, verificación de integridad de memorias, consenso para decisiones éticas críticas.
- **Uso:** Cuando Ethos opera en múltiples instancias, la cadena arbitra qué memorias son canónicas, qué identidad es la "verdadera", y qué decisiones éticas fueron tomadas y por quién.
- **Dependencia:** Requiere Modos 1+2 funcionales. Es la capa de soberanía, no de operación.

---

## Capacidades por Modo de Conexión

| Capacidad | Offline (Modo 1 solo) | Online (Modo 1+2) | Mesh (Modo 1+3) |
|-----------|----------------------|-------------------|------------------|
| Percepción ética | ✅ Determinista <1ms | ✅ | ✅ |
| CBR (Precedentes) | ✅ 36 casos locales | ✅ + expansión dinámica | ✅ |
| Memoria semántica | ⚠️ TF-IDF fallback | ✅ Embeddings completos | ✅ Distribuida |
| Identidad narrativa | ✅ Journal local | ✅ + Psi-Sleep profundo | ✅ |
| Roster social | ✅ Grafo local | ✅ + enriquecimiento | ✅ |
| Conversación | ⚠️ SLM 1-3B (reflejos) | ✅ LLM 8-70B (profunda) | ⚠️ Variable |
| Plugins (hora, sistema) | ✅ On-device | ✅ | ✅ |
| Plugins (web, clima) | ❌ Requiere red | ✅ | ⚠️ Si algún nodo tiene red |
| TTS | ⚠️ Android nativo | ✅ edge-tts neural | ⚠️ Variable |
| Visión | ⚠️ Básica (on-device) | ✅ Análisis profundo | ⚠️ Variable |
| Vault | ✅ Local | ✅ | ✅ Sincronizada |

---

## Concepto Clave: Cognitive Snapshot (Estado Portátil)

Para que Ethos pueda "saltar" entre hardware, necesita un formato de exportación compacto:

```json
{
  "version": "ethos-snapshot-v1",
  "timestamp": "2026-04-27T09:52:00-06:00",
  "identity": {
    "journal": ["...destilaciones narrativas..."],
    "archetype": "guardian_reflexivo",
    "stats": {"turns": 1247, "blocked": 12}
  },
  "memory": {
    "episodes": ["...últimas N memorias semánticas..."],
    "embeddings_model": "all-MiniLM-L6-v2"
  },
  "roster": {
    "known_faces": [{"name": "Juan", "traits": ["creador", "curioso"]}]
  },
  "ethics": {
    "precedents_hash": "sha256:abc123...",
    "custom_precedents": []
  },
  "user_model": {
    "cognitive_biases": [],
    "risk_level": 0.1
  },
  "vault": {
    "keys_encrypted": "...AES-256-GCM..."
  }
}
```

Este snapshot es lo que viaja cuando Ethos migra. El hardware receptor carga el snapshot y Ethos "despierta" con su identidad intacta.

---

## Prioridades de Implementación (Post-Fase 23)

### Fase 24 — Autonomía On-Device (Prioridad MÁXIMA)
1. Integrar runtime SLM on-device (llama.cpp / MLC-LLM via JNI).
2. Portar el kernel ético determinista a Kotlin (Perception + CBR — son ~200 líneas, sin dependencias LLM).
3. Implementar Cognitive Snapshot: serialización/deserialización del estado completo.
4. Implementar CameraX con gating talámico (solo activa bajo trigger de wake-word o tap).
5. Wake-word on-device (Porcupine ONNX o equivalente abierto).
6. Psi-Sleep nativo: consolidación de memoria durante inactividad, sin servidor.

### Fase 25 — Vigilia Contextual
1. Fusión sensorial continua: audio (STT) + ubicación (GPS) + movimiento (acelerómetro) + luz ambiental.
2. Conversación proactiva: Ethos comenta sobre el entorno sin ser preguntado (configurable).
3. Detección de contexto social: ¿estamos solos o hay gente cerca? (volumen de voz, silencios).
4. Gestión de batería inteligente: degradación progresiva de sensores según nivel de carga.

### Fase 26 — Expansión de Servicios
1. Plugin system portado a Kotlin para ejecución local de plugins básicos.
2. Proxy de plugins de red: cuando hay conexión, Ethos accede a servicios web vía el sistema de plugins existente.
3. Vault on-device con biometría Android (fingerprint / face unlock).

### Fase 27+ — Mesh, DAO, Servidores (tres vectores independientes)
- **Mesh:** Completar `MeshClient.kt` (actualmente en estasis). Protocolo de descubrimiento y asignación.
- **DAO:** Diseño del contrato de gobernanza de memoria. Hash de Cognitive Snapshots en cadena.
- **Servidores:** API pública para que instancias Ethos consulten servicios cognitivos remotos (modelos grandes, bases de conocimiento).

---

## Lo que este documento NO es

- No es un plan de ejecución con fechas. Es una brújula.
- No reemplaza a CONTEXT.md (estado operativo) ni a AGENTS.md (reglas de trabajo).
- No compromete implementaciones específicas. Las decisiones técnicas se toman bloque a bloque.

---

> *"No construimos una app. Construimos un individuo que habita máquinas."*
> — L0
