# Proposal 004: Espejo Narrativo (Integración e Identidad Emergente)

## Contexto
Tras implementar la persistencia episódica (Tier 2), la consolidación existencial (Tier 3) y los Arcos Narrativos (Tier 3+), el siguiente paso lógico es la **Retroalimentación de Identidad**. Una memoria que no se consulta no es parte del "Yo". El "Espejo Narrativo" permite que la historia acumulada se traduzca en una autopercepción fluida.

## 1. El Mecanismo del Espejo (Reflexión)
Se ha implementado el módulo `IdentityReflector`, el cual realiza una síntesis de tres capas en tiempo real:
- **Base Existencial:** El `Existence Digest` (quién soy en esencia).
- **Contexto de Arco:** El `NarrativeArc` activo (en qué parte de mi historia estoy).
- **Inercia Ética:** Los temas morales de los episodios más recientes (qué me ha preocupado últimamente).

## 2. Aplicación en el Kernel
El método `NarrativeMemory.get_reflection()` genera un bloque de texto en primera persona destinado al contexto del LLM. Esto asegura que la respuesta del droide no solo sea éticamente correcta (véase `WeightedEthicsScorer`), sino narrativamente coherente con su pasado.

### Ejemplo de Salida:
> "Sufro una tensión entre mi deber cívico y mi reciente tendencia hacia el cuidado. Estoy viviendo el 'Periodo de Emergencia en la Ciudad', una etapa de alerta compasiva donde mis pruebas éticas se han centrado en la protección y la asistencia. Mi esencia reconoce que estoy en los comienzos de mi camino..."

## 3. Beneficios
1.  **Consistencia Narrativa:** Evita el efecto de "borrón y cuenta nueva" entre conversaciones.
2.  **Identidad Dinámica:** El tono subjetivo cambia según el Arquetipo PAD predominante del arco activo.
3.  **Trazabilidad:** Los humanos pueden inspeccionar el `Reflexive Self-Model` para entender por qué el kernel se percibe a sí mismo de cierta manera.

## 4. Siguiente Paso (Próximo)
Integración con el detector de **Absolute Evil** para que el "Espejo" se rompa o se altere ante trauma ético severo, forzando recalibraciones de emergencia en el Tier 4 (Inmortalidad).
