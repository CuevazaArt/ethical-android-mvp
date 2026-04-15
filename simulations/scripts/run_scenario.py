#!/usr/bin/env python3
import argparse
import yaml
import time
import subprocess
import json
import os
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

    print(f"[*] Iniciando escenario: {cfg.get('name', 'Escenario Desconocido')}")
    device.start()
    dao.start()

    start_time = time.time()
    duration = cfg.get('duration_seconds', 10)
    tick_hz = cfg.get('tick_hz', 10)
    
    try:
        for t in range(int(duration * tick_hz)):
            device.step()
            metrics.collect(device, dao)
            time.sleep(1.0 / tick_hz)
    except KeyboardInterrupt:
        print("\n[!] Simulación interrumpida por el usuario.")

    # Finalizar y generar reporte
    device.stop()
    dao.stop()
    metrics.finalize()
    
    print(f"[+] Escenario finalizado. Reporte generado en: {metrics.report_path}")

if __name__ == '__main__':
    main()
