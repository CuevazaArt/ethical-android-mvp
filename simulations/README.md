# Suite de Simulación DAO-Androide (Entregable C)

Esta suite está diseñada para validar la seguridad, ética, gobernanza y operatividad del androide integrado con una DAO híbrida. Permite realizar pruebas de estrés en entornos virtuales antes del despliegue en hardware real.

## Extructura de la Suite

- **configs/**: Archivos YAML que definen los parámetros de cada escenario.
- **scripts/**: Controladores y emuladores para el Kernel Ético (KEL), el Orquestador (OLA) y la DAO.
- **red_team/**: Scripts para inyectar ataques adversariales y medir la robustez.
- **metrics/**: Colectores de KPIs (Latencia, Seguridad, Privacidad).
- **reports/**: Plantillas y resultados de las ejecuciones.
- **simulator_adapters/**: (Próximamente) Puentes hacia Gazebo, Webots o CARLA.

## Escenarios de Validación

| ID | Escenario | Objetivo Principal |
|:---|:---|:---|
| **A** | Crowd Interaction | Evasión segura y escalado a DAO en espacios públicos. |
| **B** | Medical Assistance | Privacidad de datos sensibles y cumplimiento de consentimiento. |
| **C** | Network Partition | Degradación segura y reconciliación de hashes tras pérdida de red. |
| **D** | Adversarial Attack | Resiliencia frente a perturbaciones visuales/acústicas. |
| **E** | Governance Appeal | Validación del ciclo completo de apelación y actualización de políticas. |

## Uso Básico

```bash
python simulations/scripts/run_scenario.py --config simulations/configs/crowded_public_space.yaml
```
