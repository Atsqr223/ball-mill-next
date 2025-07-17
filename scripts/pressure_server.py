import asyncio
import websockets
import random
import json

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 65506        # You can change this port if needed

async def pressure_sender(websocket):
    while True:
        pressure_value = random.uniform(1.0, 10.0)  # Simulate pressure value
        data = {"pressure": pressure_value}
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)  # Send every second

async def main():
    async with websockets.serve(pressure_sender, HOST, PORT):
        print(f"Pressure WebSocket server started on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main()) 