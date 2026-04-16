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
- **Bloque 1.2: Evidencia Cifrada y Anchoring (REO)**
  - Tarea 1.2.1: Implementar sistema de encriptación off-chain para grabar logs del Kernel de forma segura (video/audio simulado).
  - Tarea 1.2.2: Crear el publicador de Hashes (SHA-256) hacia el smart contract (`Anchoring Registry`).
- **Bloque 1.3: Smart Contracts (Solidity Mocks)**
  - Tarea 1.3.1: Configurar contratos de Treasury, Appeal y Governance Tokens (Solo stubs iniciales en la carpeta `contracts/`).

### 🟡 Módulo 2: Simulador, Red-Teaming y Validación (Entregable C)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Dependiente de que la arquitectura Mock DAO esté estable.*

- **Bloque 2.1: Expansión de YAML Scenarios**
  - Tarea 2.1.1: Escribir las configuraciones YAML para los escenarios B (Medical Privacy), C (Network Partition), D (Adversarial) y E (Governance Appeal).
- **Bloque 2.2: Integración de Sensores Mock**
  - Tarea 2.2.1: Conectar `device_emulator.py` a flujos de datos que simulen Gazebo/CARLA.
- **Bloque 2.3: Red-Team y Defensa Adversarial**
  - Tarea 2.3.1: Extender `adversarial_image_attack.py` instalando simulaciones con `foolbox` y spoofing de comandos de voz.

### 🟢 Módulo 3: Sociabilidad Encarnada y Cinemática (S-Blocks)
*Responsabilidad: Nivel 2 (Team Cursor)*
*Dependencias: Dependiente de los módulos de Percepción Visual/Audio.*

- **Bloque 3.1: Filtros de Cinemática Suave (S7)**
  - Tarea 3.1.1: Generar filtros de aceleración en Python para emular suavidad de movimientos robóticos (Soft Robotics).
- **Bloque 3.2: Empatía Funcional y Proxémica (S8)**
  - Tarea 3.2.1: Enganchar la métrica de `social_tension` a reguladores de velocidad de aproximación del androide.
- **Bloque 3.3: Normas Locales e Identidad UchiSoto (S9)**
  - Tarea 3.3.1: Expandir base de datos relacional para incluir preferencias de "distancia personal" y "ritmo de interacción".

### 🔵 Módulo 4: Cognición Profunda (C-Blocks)
*Responsabilidad: Nivel 1 (Antigravity)*
*Dependencias: Core Kernel (Ethical priorities)*

- **Bloque 4.1: Motor de Motivación Interna (C1) [DONE]**
  - Tarea 4.1.1: Desplegar modelo de "Sentido de Propósito" y curiosidad activa (que el androide decida investigar cosas sin prompt humano). (Implementado en `MotivationEngine`)
- **Bloque 4.2: Humildad Epistémica (C3)**
  - Tarea 4.2.1: Implementar *fallback paths* donde el androide declara proactivamente "no tengo permiso para esto" en vez de derivar una solución dudosa.
- **Bloque 4.3: Identidad Migratoria e Interoperabilidad (C5)**
  - Tarea 4.3.1: Abstracción del `BodyState`. Preparar el código para que el Kernel pueda migrar entre hardware (Dron <-> Androide <-> Móvil) sin perder memoria narrativa.

### 🟣 Módulo 5: Marco Legal, Auditoría y Transparencia a Escala (G-Blocks)
*Responsabilidad: Nivel 0 (Juan) / Nivel 1 (Claude)*
*Dependencias: Definición corporativa y legal.*

- **Bloque 5.1: Exportador Inmutable de Evidencia (G3)**
  - Tarea 5.1.1: Reforzar `AuditLog` para que encripte reportes automatizados listos para auditorías externas trimestrales.
- **Bloque 5.2: Privacidad de Borde y Credenciales (G4)**
  - Tarea 5.2.1: Flujo de VC (Verifiable Credentials) para restringir acceso a logs sensibles (como la cámara en el hogar del escenario médico).

---

## 🚀 Flujo de Sincronización Recomendado

1. **Semana 1:** Antigravity (N1) trabaja el **Módulo 1** (DAO Adapters) mientras Cursor Team (N2) despliega los YAML del **Módulo 2** (Simuladores).
2. **Sincronización:** Cursor Team hace Pull Request hacia `master-cursor`. Antigravity evalúa y fusiona a `master-antigravity`.
3. **Semana 2:** Cursor Team toma el **Módulo 3** (Sociabilidad), Claude/Antigravity construyen el **Módulo 4** (Cognición).
4. **Validación N0:** Emisión de un *Release Tag* oficial por Juan antes de mover las barreras legales del **Módulo 5**.
