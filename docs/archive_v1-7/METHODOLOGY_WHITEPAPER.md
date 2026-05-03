# Token Economy V3: El Enjambre Asimétrico de IA (Metodología Operativa)

Este documento describe la arquitectura metodológica desarrollada para el proyecto *Ethos*. Define un modelo de trabajo humano-IA diseñado para maximizar la velocidad de iteración, reducir exponencialmente el consumo de tokens (costos de API) y evitar el colapso arquitectónico ("Merge Hell") en bases de código complejas.

---

## 1. Topología del Mando (Roles Definidos)

El modelo abandona el paradigma del "Copiloto conversacional" y adopta una estructura militar y jerárquica de Mando y Control (C2):

1. **L0 (El Estratega / Humano):** 
   - Autoridad absoluta. Define la visión, la arquitectura a alto nivel y asigna el "presupuesto de cómputo" (cuántos y qué tipos de agentes se usarán por ciclo).
   - *Nunca pica código directamente.* Solo aprueba y despliega.

2. **L1 (El Watchtower / IA Orquestadora):** 
   - El nodo central del IDE (ej. Gemini/Claude integrado en el editor).
   - No escribe la lógica final del producto. Su trabajo es **compilar el plan de batalla** dado por L0, generar los prompts estandarizados para el enjambre, auditar el código recibido y realizar *micro-commits* continuos para mantener el repositorio limpio.

3. **El Enjambre (Men Scouts / Agentes Desechables):** 
   - Instancias aisladas de LLMs que ejecutan tareas discretas en paralelo.
   - Operan con **contexto ciego**: no conocen la historia del proyecto ni leen todo el repositorio. Solo reciben el contexto estricto de su tarea y el contrato de entrada/salida.

---

## 2. Asignación Proactiva de Capacidad (El Ciclo de Malla)

A diferencia de pedir a la IA que "haga una tarea", L0 provisiona un presupuesto cerrado para un hito de desarrollo. Ejemplo: `asignar enjambre: 2 Opus, 2 Sonnet, 10 Flash`.

L1 toma este presupuesto y divide el trabajo en un **Grafo de Dependencias (Olas)**:

*   **Ola 1 (Arquitectos - Modelos *Thinking* / Pesados):** Modelos de altísimo razonamiento (ej. Claude 3 Opus, Gemini Ultra). Su única función es diseñar **Contratos** (JSON Schemas, Interfaces estáticas). No programan lógica.
*   **Ola 2 (Constructores - Modelos Medios):** Modelos de alta capacidad de código (ej. Claude 3.5 Sonnet). Toman los contratos de la Ola 1 y programan las tuberías complejas.
*   **Ola 3 (Infantería - Modelos *Flash* / Ligeros):** Modelos hiper-rápidos y baratos (ej. Gemini 1.5 Flash). Toman el código de la Ola 2 y generan *Unit Tests*, documentación, formateo, refactorización y corrección de linting. Realizan el 90% del volumen de trabajo.

---

## 3. Las 7 Leyes del Enjambre (Reglas de Trabajo)

Estas reglas previenen la degradación del código y las alucinaciones de la IA a gran escala:

1. **Entregar Funciones, No Código:** El éxito de un agente no se mide en líneas escritas, sino en la demostración de que la función se ejecuta (Logs, Unit Tests en verde, o capturas). Si falla, se revierte.
2. **Propiedad Absoluta (One Agent = One Block):** No hay relevos a mitad de tarea. Si un agente falla, se le envía un prompt de corrección hasta que el código compila y pasa las pruebas. No se permite dejar comentarios `// TODO` para otro agente.
3. **Poda Sin Piedad (Cero Código Muerto):** Si un archivo, bloque o rama se vuelve obsoleto, el agente tiene la orden estricta de **eliminarlo** en el mismo commit. No se comenta el código viejo. Git preserva la historia.
4. **Contexto Persistente (`CONTEXT.md`):** El repositorio mantiene un archivo maestro de 30 líneas que documenta el estado actual de las dependencias, la arquitectura y los bloques abiertos. Cualquier nueva instancia de L1 en cualquier IDE lee este archivo primero y se orienta en menos de 1 segundo.
5. **Cero Magia Negra (Aislamiento de Módulos):** Si la IA debe proponer una nueva tecnología, L0 y L1 la validan primero. Los agentes constructores tienen prohibido instalar dependencias o arquitecturas no autorizadas en su prompt.
6. **Integración Vertical (Micro-Merges):** L1 fusiona el trabajo de los agentes de forma constante. La latencia entre miembros del enjambre causa colisiones lógicas. Cada victoria aislada se commitea inmediatamente.
7. **Single Source of Truth:** Un concepto equivale a un archivo. Está estrictamente prohibido crear archivos `v2` coexistiendo con `v1`.

---

## 4. Impacto y Resultados Logrados

*   **Ahorro de API (Token Economy):** Al delegar el 90% del trabajo mecánico a modelos ligeros, los costos operativos se reducen drásticamente mientras la velocidad de escritura se multiplica.
*   **Ausencia de Alucinaciones Estructurales:** Como los agentes constructores trabajan contra contratos estáticos (Ola 1), la IA no inventa variables, nombres de clases o estructuras imprevistas.
*   **Inmunidad al "Merge Hell":** La política de *micro-commits* de L1 y la eliminación de ramas temporales mantiene el repositorio en un estado perpetuo de "Listo para Producción" (`main` branch única).
