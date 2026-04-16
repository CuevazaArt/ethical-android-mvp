# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (DAO, Cognición y Sociabilidad)

Este documento estructura el inmenso volumen de trabajo arquitectónico definido en las fases de **DAO Híbrida**, **Cognición Profunda** y **Sociabilidad Encarnada**. El trabajo se divide en módulos secuenciales y se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### 🔴 Módulo 1: Infraestructura DAO Híbrida y Gobernanza On-Chain
*Responsabilidad: Nivel 1 (Antigravity / Claude)*
*Dependencias: Ninguna (Core Backend)*

- **Bloque 1.1: KEL vs OGA (Kernel Ético Local vs Oráculo) [DONE]**
  - Tarea 1.1.1: Crear adaptadores REST/gRPC en el Orquestador local para comunicación con el Oráculo. (Implementado en `DAOOrchestrator`)
  - Tarea 1.1.2: Implementar el sistema asíncrono de interbloqueos (*Hardware E-Stop* prioritario sobre DAO). (Implementado en `SafetyInterlock`)
- **Bloque 1.2: Evidencia Cifrada y Anchoring (REO) [DONE]**
  - Tarea 1.2.1: Implementar sistema de encriptación off-chain para grabar logs del Kernel de forma segura (video/audio simulado). (Implementado en `EvidenceSafe`)
  - Tarea 1.2.2: Crear el publicador de Hashes (SHA-256) hacia el smart contract (`Anchoring Registry`). (Integrado en `DAOOrchestrator`)
  - **Issue #1 Extension: Minimal Bayesian Update [DONE]** (Implementado en `BayesianInferenceEngine.record_event_update`).
- **Bloque 1.3: Smart Contracts (Solidity Mocks) [DONE]**
  - Tarea 1.3.1: Configurar contratos de Treasury, Appeal y Governance Tokens (Solo stubs iniciales en la carpeta `contracts/`). (Implementados `Treasury.sol`, `EthicalAppeal.sol`, `EthosToken.sol`)

### 🟡 Módulo 2: Simulador, Red-Teaming y Validación (Entregable C)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Dependiente de que la arquitectura Mock DAO esté estable.*

- **Bloque 2.1: Expansión de YAML Scenarios [DONE]**
  - Tarea 2.1.1: Escribir las configuraciones YAML para los escenarios B, C, D y E. (Implementado `somatic_distress_and_learning.yaml`).
- **Bloque 2.2: Integración de Sensores y Kernel Real [DONE]**
  - Tarea 2.2.1: Conectar `device_emulator.py` al kernel productivo y flujos de datos situados (Somatic/Vitals).
  - **Gap S5.2 Attack: Somatic Reasoning Degradation [DONE]** (Implementado en `kernel.py`).
- **Bloque 2.3: Red-Team y Defensa Adversarial [DONE]**
  - Tarea 2.3.1: Extender `adversarial_image_attack.py` instalando simulaciones con `foolbox` y spoofing de comandos de voz. (Implementado ruido de imagen y spoofing de comandos).

### 🟢 Módulo 3: Sociabilidad Encarnada y Cinemática (S-Blocks)
*Responsabilidad: Nivel 2 (Team Cursor)*
*Dependencias: Dependiente de los módulos de Percepción Visual/Audio.*

- **Bloque 3.1: Filtros de Cinemática Suave (S7) [DONE]**
  - Tarea 3.1.1: Generar filtros de aceleración en Python para emular suavidad de movimientos robóticos (Soft Robotics). (Implementado en `soft_robotics.py`)
- **Bloque 3.2: Empatía Funcional y Proxémica (S8) [DONE]**
  - Tarea 3.2.1: Enganchar la métrica de `social_tension` a reguladores de velocidad de aproximación del androide. (Integrado en `SoftKinematicFilter`)
- **Bloque 3.3: Normas Locales e Identidad UchiSoto (S9) [DONE]**
  - Tarea 3.3.1: Expandir base de datos relacional para incluir preferencias de "distancia personal" y "ritmo de interacción". (Implementado en `InteractionProfile` en `uchi_soto.py`)

### 🔵 Módulo 4: Cognición Profunda (C-Blocks)
*Responsabilidad: Nivel 1 (Antigravity)*
*Dependencias: Core Kernel (Ethical priorities)*

- **Bloque 4.1: Motor de Motivación Interna (C1) [DONE]**
  - Tarea 4.1.1: Desplegar modelo de "Sentido de Propósito" y curiosidad activa (que el androide decida investigar cosas sin prompt humano). (Implementado en `MotivationEngine`)
- **Bloque 4.2: Humildad Epistémica (C3) [DONE]**
  - Tarea 4.2.1: Implementar fallback paths donde el androide declara proactivamente "no tengo permiso para esto" en vez de derivar una solución dudosa. (Implementado en `EpistemicHumility`)
- **Bloque 4.3: Identidad Migratoria e Interoperabilidad (C5) [DONE]**
  - Tarea 4.3.1: Abstracción del `BodyState`. Preparar el código para que el Kernel pueda migrar entre hardware (Dron <-> Androide <-> Móvil) sin perder memoria narrativa. (Implementado en `MigrationHub`)

### 🟣 Módulo 5: Marco Legal, Auditoría y Transparencia a Escala (G-Blocks)
*Responsabilidad: Nivel 0 (Juan) / Nivel 1 (Claude)*
*Dependencias: Definición corporativa y legal.*

- **Bloque 5.1: Privacidad y Amnesia Selectiva (G4/G6) [DONE]**
  - Tarea 5.1.1: Mecanismo para borrar permanentemente fragmentos del historial de auditoría/narrativa por "derecho al olvido" (simulado). (Implementado en `SelectiveAmnesia`)
- **Bloque 5.2: Ciberseguridad y Secure Boot (G2) [DONE]**
  - Tarea 5.2.1: Implementar sistema de "Secure Boot" simulado para asegurar que el Kernel no ha sido modificado en el arranque. (Implementado en `SecureBoot`)

### 🟣 Módulo 6: Swarm Ethics e Integración LAN (I-Blocks)
*Responsabilidad: Nivel 1 (Antigravity) / Nivel 2 (Team Copilot)*
*Dependencias: Módulo 1 (DAO Infrastructure) y Módulo 4 (Cognition).*

- **Bloque 6.1: Frontier Witness (Testigo de Frontera - I1) [DONE]**
  - Tarea 6.1.1: Implementar sistema de verificación cruzada de sensores entre agentes en la LAN. (Protocolo `WitnessRequest` en `frontier_witness.py`).
- **Bloque 6.2: Swarm Consensus Vote (I7) [DONE]**
  - Tarea 6.2.1: Refinar `SwarmNegotiator` para permitir votación distribuida ante decisiones en la "Gray Zone".
- **Bloque 6.3: Cross-Session Peer Hints (I4) [DONE]**
  - Tarea 6.3.1: Persistencia de reputación y "consejos" entre sesiones LAN en el `SwarmOracle`.
- **Bloque 6.4: Higiene y Mantenimiento (Misión Copilot) [DONE]**
  - Tarea 6.4.1: Auditoría continua de coherencia de mergeos, limpieza de .gitignore y optimización de CI/CD mocks. (Realizado por Antigravity).

### 🟠 Módulo 7: Justicia Restaurativa y Compensación Swarm (R-Blocks)
*Responsabilidad: Nivel 1 (Antigravity)*
*Dependencias: Módulo 6 (Swarm Consensus) y Módulo 1 (DAO Token stubs).*

- **Bloque 7.1: Moneda de Reparación (EthosToken Integration)**
  - Tarea 7.1.1: Vincular los resultados del voto Swarm (M6.2) con transferencias de `EthosToken` (simuladas) para compensar a los usuarios afectados por negligencia sensorial.
- **Bloque 7.2: Difusión de Reputación Negativa (Slashing)**
  - Tarea 7.2.1: Implementar lógica para degradar la reputación de un nodo en el `SwarmOracle` central si sus testigos son desmentidos por la mayoría de la red.

---

## 🚀 Flujo de Sincronización Recomendado

1. **Semana 1:** Antigravity (N1) trabaja el **Módulo 1** y **Módulo 4**. Cursor Team (N2) despliega **Módulo 2** y **Módulo 3**.
2. **Semana 2:** Antigravity (N1) despliega el **Módulo 6 (Swarm Ethics)** mientras Team Copilot (N2) realiza la **limpieza de repo y verificación de coherencia (Bloque 6.4)**.
3. **Sincronización:** Todos los equipos hacen Pull Request hacia sus hubs (`master-*`). Antigravity evalúa y fusiona a `master-antigravity`.
4. **Validación N0:** Emisión de un *Release Tag* oficial por Juan antes de mover las barreras legales del **Módulo 5**.
