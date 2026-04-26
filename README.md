# Ethos — Ethical Android Kernel
> An open-source cognitive kernel for building ethical, autonomous android systems.

![Tests](https://img.shields.io/badge/tests-203%20passing-brightgreen) ![License](https://img.shields.io/badge/license-Apache%202.0-blue) [![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa)](https://github.com/sponsors/CuevazaArt)

### ¿Qué es Ethos?
Un kernel Python que implementa percepción ética, memoria narrativa, identidad reflexiva y razonamiento basado en precedentes legales. Diseñado para correr localmente con Ollama (sin APIs de pago), proporciona la infraestructura cognitiva necesaria para agentes autónomos que deben operar bajo marcos éticos estrictos.

### Características principales
- 🧠 **Percepción ética determinista:** Clasificación de riesgos y valores en tiempo real (<1ms, sin necesidad de LLM).
- ⚖️ **Razonamiento basado en precedentes:** Motor CBR (Case-Based Reasoning) con 36 casos éticos pre-cargados.
- 💾 **Memoria híbrida:** Recuperación de contexto eficiente combinando Semantic Embeddings y TF-IDF.
- 🪞 **Identidad narrativa reflexiva:** Diario interno evolutivo y mecanismos de neuroplasticidad identitaria.
- 🔌 **Sistema de plugins extensible:** Integraciones listas para Clima, Web, Tiempo y Comandos de Sistema.
- 🔐 **Bóveda segura:** Gestión de secretos y estados sensibles con autorización mediante WebSocket.
- 📱 **Cliente Android nativo:** SDK Nomad para integración profunda en dispositivos móviles y robótica.
- 🧪 **Calidad de grado producción:** 203 tests exhaustivos, tipado estricto y cero importaciones legacy.

### Quick Start
Comienza a interactuar con el kernel Ethos en pocos segundos:

```bash
pip install -r requirements.txt
python -m src.chat_server
# Open http://localhost:8000
```

### Architecture
Ethos emplea una arquitectura modular inspirada en la neurociencia cognitiva, dividiendo las responsabilidades en "lóbulos" especializados (Percepción, Memoria, Ejecutivo) que se comunican a través de un bus central asíncrono. Esta estructura permite una extensibilidad total y una observabilidad profunda de cada decisión ética. Para una inmersión técnica completa, consulta el archivo [CONTEXT.md](CONTEXT.md).

### Project epochs
El proyecto ha evolucionado a través de tres eras de desarrollo bien diferenciadas. Consulta el **[Índice de Épocas](docs/EPOCH_INDEX.md)** para un mapa completo de la historia del proyecto (Pre-Alpha · Serie V1 · Serie V2 activa).

### Licensing
El proyecto utiliza una estrategia de licencia dual para proteger la soberanía del kernel mientras se fomenta el ecosistema:
- **Ethos Kernel:** [Apache 2.0](LICENSE)
- **Nomad Android SDK:** [BSL 1.1](src/clients/nomad_android/LICENSE_BSL) (se convierte a Apache después de 36 meses).
- **Models:** Propietarios.

Para más detalles, consulta nuestra [LICENSING_STRATEGY.md](LICENSING_STRATEGY.md).

### Contributing
Invitamos a desarrolladores e investigadores en ética computacional a unirse al enjambre. Revisa nuestras guías de [CONTRIBUTING.md](CONTRIBUTING.md) y el protocolo de agentes en [AGENTS.md](AGENTS.md) para empezar.

### Support the Project
Si crees en un futuro donde la inteligencia artificial sea intrínsecamente ética y soberana, considera apoyar nuestro desarrollo continuo.

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?style=for-the-badge)](https://github.com/sponsors/CuevazaArt)
