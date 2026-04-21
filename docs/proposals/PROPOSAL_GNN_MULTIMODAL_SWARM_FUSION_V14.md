# PROPOSAL: Hito 14.x - GNN Multimodal Swarm Fusion (Factor Graph & SpMM)

**Date**: 2026-04-20
**Scope**: Architecture, Distributed Justice, PnP Swarm Telemetry
**Status**: DRAFT / RESEARCH
**Authors**: Antigravity (L1) / Cuevaza (L0)

## 1. Abstract
Con la consolidación de la arquitectura cuatrilobulada y el *Mind-Sync* asíncrono (Hito 13.3), el Ethos Kernel presenta una limitante natural de escalabilidad frente al **Consenso Cívico Multi-Agente (Swarm)**: la agregación de diversidades (es decir, datos liminales disonantes provenientes de múltiples sensores y Agentes Nómadas simultáneos) abrumará los cuellos de botella de tokens de Inferencia LLM.
Este documento propone resolver la saturación textual estructurando la cognición comunitaria del Kernel a través de un **Modelo Factorizable GNN**, ejecutando inferencias de Paso de Mensajes (Message Passing) aceleradas por multiplicaciones de matrices dispersas (SpMM).

---

## 2. Representación Matemática (El Factor Graph)
En nuestro modelo Swarm, proyectaremos un Grafo Mixto $G = (\mathcal{V}, \mathcal{E})$:
*   $\mathcal{V}_A$: Subconjunto de Nodos que representan los Agentes (ej. Lóbulo Compasivo, Lóbulo Pragmático, o bien, *Vessel Nomad 1, Vessel Nomad 2*).
*   $\mathcal{V}_D$: Subconjunto de Nodos que representan las Diversidades (ej. Anomalía de Tensión Límbica, Ruido Ambiental, Distancia Uchi/Soto).
*   $\mathcal{E}$: Aristas incidentes que modelan en qué grado un agente percibe u opera sobre cierta área de diversidad.

Para conseguir que las creencias se alineen antes de forzar al Lóbulo Ejecutivo (LLM) a redactar la solución, introducimos una red convolucional sobre grafos (GCN).

---

## 3. Relevancia Computacional: La Multiplicación de Matrices (SpMM)

La espina dorsal computacional que hace que este modelo sea factible para dispositivos de borde (Teléfonos Android Nómadas) y no requiera un servidor GPU de la NASA, recae en la **optimizacíón de la Ecuación del Mensaje**:

$$ H^{(l+1)} = \sigma \left( \tilde{A} H^{(l)} W^{(l)} \right) $$

Donde:
*   $\tilde{A}$ The matriz de conectividad normalizada (Quién habla con quién).
*   $H^{(l)}$ La matriz de estados/características de la capa actual (embeddings de sensores PAD).
*   $W^{(l)}$ Los Pesos Relacionales (las creencias éticas aprendibles de los factores).

### 3.1. Agregación Eficiente vs Dense Overhead
Si tenemos decenas de sensores y agentes, una matriz de conectividad Densa llenaría rápidamente decenas de Megabytes de memoria en operaciones $N \times N$, la mayoría llenas de Ceros (pues no todo agente está prestando atención al termómetro en un momento dado). 
La solución instrumentable consiste en utilizar **Sparse Matrix-Dense Matrix Multiplication (SpMM)**. Al almacenar la matriz $A$ en formatos optimizados para escasez espacial como CSR (Compressed Sparse Row) o COO, la agregación relacional se ejecuta en un orden de complejidad casi lineal respecto a las conexiones locales reales.

### 3.2. Bifurcación Funcional
Podemos desacoplar la fórmula para mantener el control "simbólico":
1.  **Agregación Lineal Rápida** ($\tilde{A}H$): Combina de forma ultra-eficiente el contexto bruto a través de Tensor Cores o paralelismo CPU simple en Android.
2.  **Transformación Probabilística** ($W, \sigma$): Pasa por un Módulo Bayesiano, que nos reporta de forma auditiva matemática (Varianza, Log-Likelihood) si la Red Neural ha llegado al **Consenso Seguro** o requiere derivado Judicial Extrema.

---

## 4. Implementación y Hoja de Ruta (CTDE)

Toda nuestra logística de Swarm actual será modificada para aprovechar el **Centralized Training, Decentralized Execution (CTDE)**:

*   **Fase 1: Prototipo Denso (Validación de Grafo)** 
    Se incrustará un Tensor Graph denso como "Thalamus secundario" en el Kernel dentro de simulación (Completado conceptualmente). Se ajustarán las Funciones de Pérdida combinando Probabilidad (log-likelihood Bayesiano) y Comportamiento Moral Esperado. 
*   **Fase 2: Adopción SpMM y Optimizaciones Edge**
    Reescribir el paso de mensajes en LibTorch/ONNX forzando el formato Sparse (COO). Esto reduce la "Latencia de Pensamiento" de ~200ms a menos de ~8ms en memoria RAM móvil.
*   **Fase 3: CTDE Flow**
    - *Entrenamiento Centralizado*: En `master-antigravity`, la macro-GNN aprende la matriz $W$ observando cientos de miles de interacciones de los Nómadas contra simuladores sociales.
    - *Ejecución Descentralizada*: La matriz $W$ destilada se carga directamente a memoria en los teléfonos físicos Nómadas. Allá, operan de manera ultraligera multiplicando matrices dispersas $A$ que se llenan a tiempo real con los valores de la batería, cámara, audio y variables límbicas, rebotando inferencias rápidas y esquivando al LLM de forma segura.
