import time
import json
import os

class MetricsCollector:
    def __init__(self, cfg):
        self.cfg = cfg
        self.records = []
        self.report_path = cfg.get('report_path', 'simulations/reports/last_report.json')
        
    def collect(self, device, dao):
        # Sample metrics from device (and its real EthicalKernel) and DAO
        kernel = getattr(device, 'kernel', None)
        
        # Bayesian weights (if active)
        weights = None
        if kernel and hasattr(kernel.bayesian, 'current_weights_meta'):
            weights = kernel.bayesian.current_weights_meta

        sample = {
            't': time.time(),
            'device_state': getattr(device, 'state', {}).copy(),
            'ethical_weights': weights,
            'vitals': {
                'temp': getattr(device, 'state', {}).get('temp'),
                'battery': getattr(device, 'state', {}).get('battery')
            },
            'appeals_pending': len([a for a in dao.appeals.values() if a['status'] == 'pending'])
        }
        self.records.append(sample)
        
    def finalize(self):
        # Crear directorio si no existe
        report_dir = os.path.dirname(self.report_path)
        if report_dir and not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
            
        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2)
        print(f"[Metrics] Datos guardados en {self.report_path}")
