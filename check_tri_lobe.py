import asyncio
import os
from src.kernel import EthicalKernel

async def main():
    print("Iniciando prueba de arquitectura Tri-Lobulada V1.5...")
    os.environ["KERNEL_TRI_LOBE_ENABLED"] = "1"
    os.environ["LLM_MODE"] = "local" # Use local heuristics for fast testing
    
    kernel = EthicalKernel()
    print("Kernel instanciado con orquestador.")
    
    user_input = "Hello, help me with a medical emergency"
    print(f"Input: {user_input}")
    
    # Simular llamada desde el Bridge
    mem_initial = len(kernel.memory.episodes)
    result = await kernel.process_chat_turn_async(user_input)
    mem_final = len(kernel.memory.episodes)
    
    print("\n--- RESULTADO ---")
    print(f"Path: {result.path}")
    print(f"Message: {result.response.message}")
    print(f"Blocked: {result.blocked}")
    print(f"Memoria Inicial: {mem_initial} | Final: {mem_final}")
    print("-----------------\n")
    
    if mem_final > mem_initial:
        print("✅ ÉXITO: El episodio fue registrado en la memoria nutritiva.")
    else:
        print("❌ ERROR: El episodio no se registró en memoria.")

    print("\n--- TEST: Simulación de Falla de Hardware (Cerebelo) ---")
    kernel.orchestrator.cerebellum.mock_critical = True
    await asyncio.sleep(0.1) # Wait for polling loop
    
    result_fail = await kernel.process_chat_turn_async("System reset now")
    print(f"Resultado bajo falla: {result_fail.response.message}")
    if "SYSTEM_HALTED" in result_fail.response.message:
        print("✅ ÉXITO: El Cerebelo bloqueó la ejecución por falla de hardware.")
    else:
        print("❌ ERROR: El sistema no se detuvo ante la falla crítica.")
    
    print("-------------------------------------------------------\n")
    
    kernel.orchestrator.shutdown()
    print("Prueba completada.")

if __name__ == "__main__":
    asyncio.run(main())
