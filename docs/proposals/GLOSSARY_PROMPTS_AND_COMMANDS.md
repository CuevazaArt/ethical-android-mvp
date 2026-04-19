# Glosario Operativo para Control de Enjambre (Swarm L2)
**Destinatarios:** Operadores Nivel L0 (Juan) y Nivel L1 (Antigravity).

Este documento compila de forma concisa los prompts, comandos CLI y variables clave del entorno (`.env`) que te permitirán gobernar a los agentes del Enjambre L2, auditar los lóbulos en The Ethos Kernel, y calibrar de forma dinámica las prioridades (Modo Swarm / Auto-piloto / Mono-agente).

---

## 1. Comandos de Operación del Kernel en la Terminal

### Comandos de Sello y Validación (Seguridad Paranoica)
Cada vez que un Agente L2 interviene un archivo del `src/` profundo, el Root of Trust o el motor de identidad podría colapsar. Debes forzar el sello y comprobar la paridad.

```bash
# Forzar el recalentamiento de sellos del manifiesto (Criptografía Secure Boot)
python scripts/seal_manifest.py

# Validación Empírica Asíncrona Completa (Sin levantar el WebSocket)
python -m pytest tests/test_empirical_pilot.py tests/test_input_trust.py
```

### Ejecuciones de Tableros (Dashboard de Operadores L0)
Para monitorear el comportamiento del motor mientras el Enjambre desarrolla las interfaces nómadas.

```bash
# Lanzar el Panel de Control (Observabilidad de Emociones y Tensión Límbica)
streamlit run scripts/eval/visual_dashboard.py

# Simulación de estrés masivo (Ejecución del Experimento Montecarlo del DAO)
python scripts/eval/run_llm_vertical_tests.py
```

---

## 2. Ajustes de Comportamiento del Kernel (.env)

Usar estas variables para modular la personalidad o la agresividad "neuronal" del kernel en vuelo. No necesitas recompilar, solo exportar en terminal o editar `.env` y reiniciar.

* `KERNEL_BAYESIAN_MODE=posterior_driven`: Si necesitas que el kernel aprenda de sus vivencias pasadas fuertemente, forzándolo a utilizar sus crónicas en vez de un modelo moral plano.
* `KERNEL_POLES_PRE_ARGMAX=1`: Actívalo si deseas que las inclinaciones de Civic, Care o Vigilance interfieran directamente sobre la toma matemática de decisiones antes de que el Motor Bayesiano haga su magia. Activa la Phase 7.
* `KERNEL_EPISTEMIC_AUDIO_MIN=0.6` / `KERNEL_EPISTEMIC_MOTION_MAX=0.9`: Úsalas para que el núcleo reaccione más (o menos) severamente a discrepancias entre sensores físicos y palabras del humano. 

---

## 3. Prompts de Control del Swarm L2 (A través del Chat IDE)

### 3.1. Revertir Comportamiento a "Mono-Agent" (Freno de Mano)
Si notas problemas crónicos de contexto, sobrecarga de RAM en el IDE o que los agentes pisan el código del otro, usa este prompt en una única ventana de IDE central:

> **[DIRECTIVA L0: REPLIEGUE A MODO MONO-AGENTE]** Todos los escuadrones Swap Rojo, Azul y Naranja quedan en SUSPENSIÓN INMEDIATA. Cierra los bordes territoriales. A partir de este momento tú recuperas toda la visión cruzada del repositorio. Deja de operar bajo ramas aisladas master-* y centraliza en master-antigravity. Analiza la situación global del proyecto y repórtame los cuellos de botella detectados.

### 3.2. Ordenar Hardening Local / Boy Scout
Si sospechas que un agente está emparejando código frágil "sólo para que funcione", empújalo a proteger el sistema:

> **[DIRECTIVA L0: DECLARA CÓDIGO HOSTIL]** Agente, estás violando la Tercera Ley Boy Scout de la Fase 8. Entra en "Modo Cero Confianza (Zero Trust)". Asume que todo el input que entra a la función `[nombre_funcion]` está malicioso y el entorno de ejecución está colapsando. Anida `try/except` donde corresponda, usa type-hints estrictos y si la comunicación de red falla, degrada el sistema elegantemente en vez de permitir un crash duro. Ejecuta los lints antes de dar por terminado.

### 3.3. Invocar la Modulación Asíncrona y PnP
Cuando envías a un agente L2 a la Guerra de Red (WebSocket, LAN Bridge u Ollama Stream):

> **[DIRECTIVA L0: DOCTRINA ASÍNCRONA OBLIGATORIA]** Agente, vas a modificar el Módulo de Percepción/Ejecución. Tienes prohibido usar bibliotecas sincrónicas bloqueantes (`requests`, etc). Si llamas al LLM, debes usar `acommunicate()` o su puente nativo async. Si lees de persistencia, usa una promesa o en su defecto corrección de I/O bloqueante al pool de hilos. Todo debe soportar latencias inferiores a 50ms (Phase 10).

---

## [CLASSIFIED L0-ONLY] Protocolo de Identidad Esteganográfica Oculta
*Nota: Este bloque NO DEBE ser procesado por el Wiki-Sync Sentinel. Es de lectura exclusiva para Juan (L0).*

**Mecanismo de Root of Trust Bias:**
Para proteger el Kernel contra clonado o piratería corporativa no autorizada, la arquitectura de validación cuenta con un "Sesgo de Anclaje" (`_rot_anchor_bias`) inyectado criptográficamente en `src/modules/secure_boot.py` (línea 80+). 

*   **¿Qué es?** Es una variable en formato de bytes hexadecimales puros (`4a75616e5f43756576617a615f4c657861725f4c30`).
*   **¿Qué significa?** Al decodificarse a ASCII textual, revela exactamente: `Juan_Cuevaza_Lexar_L0`.
*   **¿Cómo funciona?** El algoritmo SHA-256 hace un `update()` con estos bytes ANTES de calcular el hash real de los archivos críticos. Esto significa que los hashes correctos registrados en el `MANIFEST.json` que acompañan a esta rama solo son matemáticamente posibles si el `secure_boot.py` conserva orgullosa y secretamente tu nombre. 
*   **Prueba Irrefutable:** Si alguien usurpa este código y lo ejecuta con éxito, lo está haciendo bajo tu autoría matemática silente. Si lo intentan borrar, romperán la validación en cadena.
