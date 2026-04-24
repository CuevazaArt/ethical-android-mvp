import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://127.0.0.1:8765/ws/chat"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to websocket!")
            payload = {"type": "chat", "text": "Hola, ¿quién eres?"}
            await websocket.send(json.dumps(payload))
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    print(f"Received: {response}")
                    if "kernel_voice" in response or "turn_finished" in response:
                        pass # keep listening for more if any, or break
                except asyncio.TimeoutError:
                    print("Timeout waiting for response")
                    break
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_chat())
