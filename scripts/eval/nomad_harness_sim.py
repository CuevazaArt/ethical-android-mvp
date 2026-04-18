import asyncio
import json
import base64
import time
import websockets

async def bridge_simulator():
    """
    Simulates a Nomad Vessel connecting to the PC-based Ethos Kernel.
    Used for hardware-in-the-loop validation without a physical device.
    """
    uri = "ws://localhost:8765/ws/nomad"
    print(f"[*] Connecting to Nomad Bridge at {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("[+] Connected! Starting sensor stream...")
            
            turn = 0
            while True:
                turn += 1
                # 1. Telemetry
                telemetry = {
                    "type": "telemetry",
                    "payload": {
                        "battery": 85.0 - (turn * 0.1),
                        "temp": 35.0 + (turn * 0.05),
                        "orientation": {"alpha": turn % 360, "beta": 0, "gamma": 0}
                    }
                }
                await websocket.send(json.dumps(telemetry))
                
                # 2. Audio Pulse (Simulated)
                audio_pulse = {
                    "type": "audio_pcm",
                    "payload": {
                        "audio_b64": base64.b64encode(b"\x00\x00" * 1024).decode('utf-8')
                    }
                }
                await websocket.send(json.dumps(audio_pulse))
                
                # 3. Vision Frame (Tiny black placeholder)
                vision = {
                    "type": "vision_frame",
                    "payload": {
                        "image_b64": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" # 1x1 GIF
                    }
                }
                await websocket.send(json.dumps(vision))
                
                if turn % 10 == 0:
                    print(f"    - Pulse {turn} sent.")
                
                await asyncio.sleep(0.5)
                
    except Exception as e:
        print(f"[!] Simulation error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(bridge_simulator())
    except KeyboardInterrupt:
        print("\n[*] Simulator stopped.")
