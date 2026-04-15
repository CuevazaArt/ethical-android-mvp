import argparse
import time
# from device_emulator import DeviceEmulator
# from dao_emulator import DaoEmulator

def run_simulation(config_path):
    print(f"[*] Iniciando simulación: {config_path}")
    # TODO: Cargar YAML y orquestar emuladores
    time.sleep(1)
    print("[+] Escenario completado.")
    print("[+] Reporte generado en simulations/reports/last_run.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Controlador de Escenarios DAO-Androide")
    parser.add_argument("--config", required=True, help="Ruta al YAML del escenario")
    args = parser.parse_args()
    run_simulation(args.config)
