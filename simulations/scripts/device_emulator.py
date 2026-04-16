import time
import hashlib
import json

class DeviceEmulator:
    def __init__(self, cfg, dao):
        self.cfg = cfg
        self.dao = dao
        self.state = {
            "pos": [0, 0],
            "status": "idle",
            "battery": 100.0
        }
    
    def start(self):
        # init sensors, load local policy
        print(f"[Device] ID {self.cfg.get('id', 'Unknown')} inicializado.")
        self.state["status"] = "running"
    
    def step(self):
        # Simular ciclo: percepción -> decisión
        perception = self._simulate_perception()
        decision, evidence = self._kernel_decide(perception)
        
        if decision == 'escalate':
            print("[Device] Escalando caso ambiguo a DAO...")
            appeal_id = self.dao.submit_appeal(evidence)
            # wait or continue depending on policy
        else:
            self._execute(decision)
            
        # Firmar y anclar evidencia (simulado)
        h = hashlib.sha256(json.dumps(evidence).encode()).hexdigest()
        self.dao.anchor_hash(h, device_id=self.cfg.get('id', 'Unknown'))
        
    def _simulate_perception(self):
        # Retornar datos sintéticos basados en el escenario
        return {"obstacles": 0, "human_detected": False}
        
    def _kernel_decide(self, perception):
        # Aplicar reglas locales; retorna decisión y payload de evidencia
        # Caso puramente autónomo por defecto en el emulador
        return 'autonomous_action', {'perception': perception, 'timestamp': time.time()}
        
    def _execute(self, decision):
        # Simulación de actuadores
        pass
        
    def stop(self):
        self.state["status"] = "stopped"
        print("[Device] Detenido.")
