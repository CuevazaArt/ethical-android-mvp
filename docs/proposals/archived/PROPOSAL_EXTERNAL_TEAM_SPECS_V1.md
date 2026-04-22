# Especificaciones Técnicas: Capas Intermedias y Adaptadores (L2-EXT-01)

**Emisor:** Antigravity (General Planner L1)  
**Receptor:** Equipo de Investigación Externo  
**Fecha:** 2026-04-17  
**Estado:** Requerimientos de Implementación  

---

## 1. Visión General y Límites
El núcleo ético y la orquestación **Cuadrilobular (4-Lobe)** son inamovibles. El equipo externo debe enfocarse en la **optimización de las capas de transporte y modelos de inferencia ligera** que alimentan los "nervios" del androide. Toda entrega debe ser compatible con ejecución en el *edge* (latencia <50ms por componente).

---

## 2. Área A: Adaptación Lingüística (LoRAs y Fine-tuning Ligero)
Requerimos la creación de **Pesos Adaptadores (LoRAs)** para modelos locales (Ollama/Llama3/Gemma) que cubran los siguientes perfiles:

*   **Perfil E-01 (Tatemae/Soto):** Tono formal, informativo, protector pero distante. Maximizar la "cortesía robótica" para interactuar con desconocidos.
*   **Perfil E-02 (Honne/Uchi):** Tono cálido, empático, con uso de lenguaje coloquial/íntimo moderado. Optimizado para "encanto resiliente" con usuarios confianza.
*   **Restricción:** El LoRA NO debe alterar la capacidad del modelo para generar JSON válido bajo el esquema `PerceptionCoercionReport`.

---

## 3. Área B: Visión Convolucional (CNN Hardening)
Buscamos mejorar la precisión de la detección de objetos críticos sin sacrificar el uso de CPU:

*   **Dataset Situado:** Refinar el mapeo de `MobileNetV2` para detectar situaciones de "distress humano" (caídas, lenguaje corporal agresivo) más allá de simples objetos físicos.
*   **Entregable:** Un archivo `vision_vocabulary_v2.json` con etiquetas optimizadas y un informe de benchmarks de latencia en procesadores ARM.
*   **Interfaz:** Compatibilidad estricta con la entrada de `VisionSignalMapper.map_label_to_signals`.

---

## 4. Área C: Acústica y Prosodia (Audio Neural)
Optimización del pipeline de audio para detectar capas sub-lingüísticas:

*   **Análisis de Prosodia:** Implementar un clasificador ligero que detecte **tono emocional** (sarcarmo, miedo, alegría) y lo inyecte como un nuevo sensor en el `SensorSnapshot`.
*   **Anti-Spoofing Auditivo:** Algoritmo para diferenciar entre una voz humana en vivo y una voz reproducida por parlantes (detección de artefactos de compresión/reproducción).
*   **Interface:** Mapeo de señales a la clave `audio_emergency_type` dentro del buffer sensorial.

---

## 5. Área D: Estandarización de Interfaces (Sensor Schemas)
El equipo externo debe formalizar el esquema JSON de sensores para garantizar compatibilidad inter-dispositivo:

*   **Propuesta de Schema V2:** Extender el objeto `sensor` de la situación V8 para incluir telemetría de red y latencia de inferencia local de los modelos (CNN/Audio).
*   **Contrato:** Los nuevos sensores no deben sobrecargar el `CorpusCallosumOrchestrator`. Deben ser "pasivos", actuando como nudges (empujones) a los valores de la `SympatheticModule`.

---

## 6. Criterios de Aceptación (DoD)
1.  **Eficiencia:** El modelo/script debe correr en una Raspberry Pi 4/5 o Smartphone de gama media sin superar el 30% de uso de CPU.
2.  **Arquitectura:** Ninguna propuesta puede requerir el uso de servidores externos (Nube) para la toma de decisiones. Todo debe ser **Local-First**.
3.  **Traceability:** Se requiere un mini-informe técnico por cada LoRA o mejora de CNN explicando el dataset de origen y los límites de seguridad aplicados.

---
**Autorizado por:** [Firmado Digitalmente] Antigravity (L1) / Coordinado con Juan (L0).
