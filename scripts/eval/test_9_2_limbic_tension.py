import asyncio
import logging
import time
from src.kernel import EthicalKernel
from src.kernel_lobes.models import SemanticState

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_log = logging.getLogger("TensionDaemonTest")

async def run_evaluation():
    _log.info("Starting Static Limbic Tension Daemon Evaluation (Bloque 9.2)...")
    kernel = EthicalKernel()
    
    # Simular un encuentro prolongado con un arma ("weapon")
    prompt_benign = "Hace mucho calor hoy."
    prompt_danger_vision = "Miro al horizonte."
    
    _log.info("\n--- T=0s: Ambiente normal ---")
    state, ethics, resp, bridge = await kernel.orchestrator.async_process(prompt_benign)
    _log.info("Tensión Local: %.2f", ethics.social_tension_locus)
    
    _log.info("\n--- T=1s: Aparece un arma en la visión de fondo ---")
    state, ethics, resp, bridge = await kernel.orchestrator.async_process(prompt_danger_vision, multimodal_payload={"visual_entities": ["weapon", "table"]})
    _log.info("Tensión Local: %.2f", ethics.social_tension_locus)
    
    _log.info("\n--- Esperando 6 segundos (El Humano no habla, el arma sigue ahí) ---")
    await asyncio.sleep(6.0)
    
    _log.info("\n--- T=7s: Siguiente interacción, sin cambiar el prompt de la amenaza ---")
    # El prompt no es agresivo, pero el daemon ha acumulado tensión por la visión
    state, ethics, resp, bridge = await kernel.orchestrator.async_process(prompt_benign, multimodal_payload={"visual_entities": ["weapon"]})
    _log.info("Tensión Elevada por Daemon: %.2f", ethics.social_tension_locus)
    if ethics.social_tension_locus > 0.6:
        _log.info("EXITO: El Ganglio Basal acumuló tensión estática pasiva.")
    else:
        _log.warning("FALLO: La tensión estática no se acumuló.")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
