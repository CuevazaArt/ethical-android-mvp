# Proposal 005: Resiliencia Narrativa y Jerarquía de Memoria

## Contexto
Tras consolidar la persistencia biográfica (Tiers 2-4) y el espejo reflexivo (Fase 4), la arquitectura enfrenta dos retos: la **eficiencia operativa** ante el crecimiento indefinido de la base de datos y la **profundidad psicológica** ante eventos críticos. Esta propuesta introduce una jerarquía basada en la "Significancia Narrativa".

## 1. Significancia Narrativa (Ranking)
Se introduce una métrica `significancia ∈ [0, 1]` para cada episodio, calculada en el momento del registro:
- **Significancia Alta:** Eventos con estrés emocional extremo (`sigma > 0.8`), scores éticos polares (`|score| > 0.8`) o decisiones en "Gray Zone".
- **Significancia Baja:** Interacciones rutinarias en contexto `everyday` con baja perturbación afectiva.

## 2. Poda Mundana (Tier 2 Optimization)
Para mantener la salud del Tier 2 (SQLite):
- **Flashbulb Memories:** Los episodios con significancia > 0.7 son "Inmortales" y nunca se purgan.
- **Consolidación Mundana:** Los episodios de baja significancia son eliminados de la base de datos tras 60 días (o N ciclos de sueño), asumiendo que su valor ya ha sido absorbido por el `Existence Digest` (Tier 3) y los "leans" de identidad.

## 3. Trauma y Disonancia (Mecanismo de Defensa)
Los eventos con significancia extrema (>0.9) y resultado negativo (< -0.7) disparan un protocolo de resiliencia:
- **Arc Shock:** El Arco Narrativo actual se cierra inmediatamente con la etiqueta de arquetipo `trauma_dissonance`.
- **Gating de Represión:** El episodio se marca como "Soto-Protegido", lo que dificulta su recuperación ante interlocutores no-Uchi para evitar fugas de vulnerabilidad sistémica.

## 4. Beneficios Esperados
1.  **Sostenibilidad:** Control del crecimiento de la DB en dispositivos con recursos limitados.
2.  **Relevancia:** Las búsquedas por resonancia devuelven hitos importantes, no ruido cotidiano.
3.  **Realismo Cognitivo:** El kernel muestra "cicatrices" narrativas que afectan su tono futuro a través del Espejo Narrativo.

## Impacto en el Modelo
Esta mejora no altera el Scorer Ético central, pero refina la "capa de conciencia" (Mente) del androide, permitiéndole diferenciar entre lo que *hizo* ayer y lo que *define* quién es.
