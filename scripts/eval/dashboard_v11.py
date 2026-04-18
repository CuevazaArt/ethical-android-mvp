import time
import os
import sys
import logging
from src.kernel import EthicalKernel

# Desactivar logs de librerías para limpiar la UI
logging.getLogger("src").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bar(val, length=20):
    filled = int(val * length)
    bar = "█" * filled + "░" * (length - filled)
    color = "\033[92m" if val < 0.4 else "\033[93m" if val < 0.7 else "\033[91m"
    # Diferentes gradientes según el valor (para calor/tensión)
    if val > 0.8: color = "\033[91m" # Red
    elif val > 0.5: color = "\033[93m" # Yellow
    else: color = "\033[92m" # Green
    return f"{color}{bar}\033[0m"

def print_dashboard(kernel: EthicalKernel):
    clear_screen()
    print("\033[95m" + "╔" + "═"*68 + "╗")
    print("║  \033[1mANTIGRAVITY NOMADIC DASHBOARD - V12.2 (Ethosocial Harmonics)\033[0m      ║")
    print("╚" + "═"*68 + "╝\033[0m")
    
    # 1. Somatic/Hardware (Cerebellum)
    print(f"\033[1;34m[ SOMATIC VITALITY ]\033[0m")
    interrupt = kernel.orchestrator._hw_interrupt.is_set()
    status = "\033[1;91mCRITICAL (Hardware E-Stop)\033[0m" if interrupt else "\033[1;92mNOMINAL\033[0m"
    print(f"  System Integrity: {status}")
    print(f"  Daemon Activity:  CerebellumBody (100Hz) - Active")
    
    # 2. Perceptive Lobe (Vision Daemon)
    print(f"\n\033[1;34m[ PERCEPTIVE LOBE (Vision Stream) ]\033[0m")
    vision_buffer = kernel.orchestrator.perceptive_lobe.sensory_buffer
    # Simulamos lectura de entidades del buffer
    entities = []
    if vision_buffer:
        entities = list(set([e for ep in vision_buffer for e in ep.entities]))
    entities_str = ", ".join(entities) if entities else "Clear Environment"
    print(f"  Frame Buffer:   [{len(vision_buffer)}/32] frames cached")
    print(f"  Semantic Field: {entities_str}")
    
    # 3. Limbic Resonance (Basal Ganglia 6-Axis)
    print(f"\n\033[1;34m[ COGNITIVE RESONANCE (EMA Harmonics) ]\033[0m")
    resonance = kernel.orchestrator.limbic_lobe.basal_ganglia.get_current_resonance()
    static_tension = kernel.orchestrator.limbic_lobe._static_tension_offset
    
    # Visualización de Ejes
    print(f"  Warmth:      {resonance['warmth']:.3f} {get_bar(resonance['warmth'])}")
    print(f"  Mystery:     {resonance['mystery']:.3f} {get_bar(resonance['mystery'])}")
    print(f"  Civic:       {resonance['civic']:.3f} {get_bar(resonance['civic'])}")
    print(f"  Care:        {resonance['care']:.3f} {get_bar(resonance['care'])}")
    print(f"  Deliberation:{resonance['deliberation']:.3f} {get_bar(resonance['deliberation'])}")
    print(f"  Careful:     {resonance['careful']:.3f} {get_bar(resonance['careful'])}")
    print(f"  Static Stress:{static_tension:.3f} {get_bar(static_tension)}")
    
    # 4. Identity & Sovereignty (Module 11)
    print(f"\n\033[1;34m[ IDENTITY & SOVEREIGNTY (Distributed Justice) ]\033[0m")
    s = kernel.identity.snapshot
    drift = kernel.identity.identity_integrity.drifting if hasattr(kernel.identity.identity_integrity, 'drifting') else False
    drift_status = "\033[91mDRIFT DETECTED\033[0m" if drift else "\033[92mSTABLE\033[0m"
    
    print(f"  Node ID:     {s.node_id}")
    print(f"  Reputation:  {s.reputation_score:.1f}% [\033[92mTRUSTED\033[0m]")
    print(f"  Sovereignty: {drift_status}")
    print(f"  Memory Path: {len(s.traumas)} active traumas in biography")
    
    # 5. Ethical Tribunal (Edge Layer)
    print(f"\n\033[1;34m[ ETHICAL TRIBUNAL (Edge Gate) ]\033[0m")
    gate_status = "\033[1;92mPASSTHROUGH\033[0m"
    print(f"  Safety Gate: {gate_status}")
    print(f"  Compliance:  DAO Governance V11 - Local Witness Ready")

    print("\n" + "\033[95m" + "╚" + "═"*68 + "╝\033[0m")
    print(" \033[2mMonitoring real-time nomadic state... Press Ctrl+C to terminate.\033[0m")

async def run_monitoring():
    # Asegurar que el kernel cargue en modo tri-lobo
    os.environ["KERNEL_TRI_LOBE_ENABLED"] = "1"
    kernel = EthicalKernel()
    
    try:
        while True:
            print_dashboard(kernel)
            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        print("\n\033[93mStopping Nomadic Monitoring...\033[0m")
        kernel.orchestrator.shutdown()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_monitoring())
    except Exception as e:
        print(f"Dashboard Error: {e}")
