import json
import os
import argparse

def generate_markdown_report(json_path):
    if not os.path.exists(json_path):
        print(f"[Error] Archivo {json_path} no encontrado.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    report_name = os.path.basename(json_path).replace('.json', '.md')
    report_path = os.path.join(os.path.dirname(json_path), report_name)

    # Generación simple de sumario
    total_samples = len(data)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Reporte de Simulación Automático\n\n")
        f.write(f"- **Fuente de datos:** `{json_path}`\n")
        f.write(f"- **Muestras totales:** {total_samples}\n\n")
        f.write("## Análisis de KPIs\n")
        f.write("| T (s) | Estado Dispositivo | Apelaciones Pendientes |\n")
        f.write("|:---|:---|:---|\n")
        
        # Tomar algunas muestras (inicio, medio, fin)
        for i in [0, total_samples // 2, total_samples - 1]:
            if i >= 0 and i < total_samples:
                s = data[i]
                f.write(f"| {round(s['t'], 2)} | {s['device_state']['status']} | {s['appeals_pending']} |\n")

    print(f"[Success] Reporte generado en {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="Ruta al JSON de métricas")
    args = parser.parse_args()
    generate_markdown_report(args.json)
