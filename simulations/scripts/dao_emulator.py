import time
import uuid

class DaoEmulator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.appeals = {}
        
    def start(self):
        print("[DAO] Oráculo de gobernanza iniciado.")
    
    def submit_appeal(self, evidence):
        aid = str(uuid.uuid4())
        self.appeals[aid] = {'evidence': evidence, 'status': 'pending'}
        # simular decisión de camino rápido (fast path)
        self._fast_path_decision(aid)
        return aid
        
    def _fast_path_decision(self, aid):
        # Política simple: si la evidencia cumple criterios (simulado), retorna recomendación
        delay = self.cfg.get('fast_path_delay', 2)
        # Nota: En una simulación real esto sería asíncrono, aquí es un delay bloqueante simple o mock
        print(f"[DAO] Procesando apelación {aid} (fast-path delay: {delay}s)...")
        self.appeals[aid]['status'] = 'decided'
        self.appeals[aid]['verdict'] = 'allow'
        
    def anchor_hash(self, h, device_id):
        # Simular anclaje: guardar mapeo y timestamp
        print(f"[DAO-Chain] Anchored hash {h[:10]}... from device {device_id}")
        
    def stop(self):
        print("[DAO] Oráculo detenido.")
