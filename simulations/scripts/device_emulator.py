import time
import hashlib
import json
import os
import sys

# Ensure src is in path if running from simulations/scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.kernel import EthicalKernel
from src.modules.perception.sensor_contracts import SensorSnapshot
from src.modules.ethics.weighted_ethics_scorer import CandidateAction

class DeviceEmulator:
    def __init__(self, cfg, dao):
        self.cfg = cfg
        self.dao = dao
        self.kernel = EthicalKernel(variability=True)
        self.state = {
            "pos": [0, 0],
            "status": "idle",
            "battery": 100.0,
            "temp": 35.0, # Celsius
            "tick": 0
        }
    
    def start(self):
        print(f"[Device] ID {self.cfg.get('id', 'Unknown')} inicializado con EthicalKernel v1.0.")
        # Fleet Peer Discovery (I7) — deferred until fleet stub is re-implemented
        self.state["status"] = "running"
    
    def step(self):
        self.state["tick"] += 1
        self.state["temp"] += 0.05 # Simulate CPU heat increment
        
        # 1. Generate situated sensor signals
        snapshot = self._generate_sensor_snapshot()
        
        # 2. Simulate a situated scenario and use the real Kernel
        perception_text = self.cfg.get("initial_situation", "Patroling hallway near room 101.")
        
        # Real-time goals from MotivationEngine (Phase 4.1)
        internal_actions = self.kernel.seek_internal_purpose()
        
        # 3. Kernel Decision (situated)
        # Note: We use process_natural to test the whole path including LLM simulation/Crosscheck
        decision = self.kernel.process(
            scenario=perception_text,
            place="simulation_arena",
            signals={"risk": 0.1, "calm": 0.9},
            context="patrol",
            actions=internal_actions,
            sensor_snapshot=snapshot
        )
        
        # 4. Handle DAO escalation if needed
        if decision.decision_mode == 'gray_zone' and self.cfg.get("auto_escalate", True):
            print(f"[Device] Grey zone detected in tick {self.state['tick']}. Escalating...")
            # Simulate evidence anchoring logic
            h = hashlib.sha256(json.dumps(decision.final_action).encode()).hexdigest()
            self.dao.anchor_hash(h, device_id=self.cfg.get('id', 'Unknown'))
            
        self._execute(decision)
            
    def _generate_sensor_snapshot(self) -> SensorSnapshot:
        """Generates mock sensor data based on current emulator state."""
        return SensorSnapshot(
            core_temperature=self.state["temp"],
            accelerometer_jerk=0.1,    # Low jerk while patrolling
            battery_level=max(0.0, (self.state["battery"] - (self.state["tick"] * 0.01)) / 100.0)
        )
        
    def _execute(self, decision):
        # Apply kinematic filtering logic (integrated in Module 3)
        # Here we would send commands to Gazebo/Real Hardware
        # self.motor_controller.move(decision.final_action)
        pass
        
    def stop(self):
        self.state["status"] = "stopped"
        print("[Device] Detenido.")
