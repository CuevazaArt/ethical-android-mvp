import asyncio
import json

import websockets


async def test_streaming():
    url = "ws://127.0.0.1:8765/ws/chat"
    async with websockets.connect(url) as ws:
        # Send a message
        payload = {"text": "Hello, how are you today?", "include_narrative": False}
        await ws.send(json.dumps(payload))

        print("Sent message, waiting for events...")

        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
                event = json.loads(raw)
                print(f"Received event: {event.get('event_type') or 'FINAL/OTHER'}")
                if event.get("event_type") == "turn_finished":
                    print("Turn finished successfully.")
                    break
                if "error" in event:
                    print(f"Error: {event['error']}")
                    break
            except TimeoutError:
                print("Timeout waiting for server response.")
                break


if __name__ == "__main__":
    # Start server in background?
    # For now, assume the user runs it or I start it.
    asyncio.run(test_streaming())
