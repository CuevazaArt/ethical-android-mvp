#!/usr/bin/env python3
import argparse
import yaml
import time
import subprocess
import json
import os
import sys
import os

# Ensure the simulations/scripts and simulations/ directories are in path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(SIM_DIR)

sys.path.append(SCRIPT_DIR)
sys.path.append(SIM_DIR)
sys.path.append(ROOT_DIR)

from device_emulator import DeviceEmulator
from dao_emulator import DaoEmulator
from metrics.metrics_collector import MetricsCollector

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Controlador de Escenarios DAO-Androide")
    parser.add_argument('--config', required=True, help="Ruta al YAML del escenario")
    args = parser.parse_args()
    
    cfg = load_config(args.config)

    # Iniciar emuladores con sus secciones de config correspondientes
    dao = DaoEmulator(cfg.get('dao', {}))
    device = DeviceEmulator(cfg.get('device', {}), dao)
    metrics = MetricsCollector(cfg.get('metrics', {}))

    print(f"[*] Iniciando escenario: {cfg.get('name', 'Escenario Desconocido')}", flush=True)
    device.start()
    dao.start()

    start_time = time.time()
    duration = cfg.get('duration_seconds', 10)
    tick_hz = cfg.get('tick_hz', 2)
    
    try:
        total_ticks = int(duration * tick_hz)
        for t in range(total_ticks):
            print(f"[#] Tick {t+1}/{total_ticks}...", flush=True)
            device.step()
            metrics.collect(device, dao)
            time.sleep(1.0 / tick_hz)
    except KeyboardInterrupt:
        print("\n[!] Simulación interrumpida por el usuario.", flush=True)

    # Finalizar y generar reporte
    device.stop()
    dao.stop()
    metrics.finalize()
    
    print(f"[+] Escenario finalizado. Reporte generado en: {metrics.report_path}", flush=True)

if __name__ == '__main__':
    main()
