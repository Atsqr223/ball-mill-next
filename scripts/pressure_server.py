import asyncio
import websockets
import json

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 65506      # Change if needed

daq_client = None
frontend_clients = set()

async def handler(websocket, path):
    global daq_client
    # Wait for registration message
    try:
        reg_msg = await websocket.recv()
        reg_data = json.loads(reg_msg)
        if reg_data.get('type') == 'registerDAQ':
            daq_client = websocket
            print("DAQ client connected.")
            # Now listen for pressure data from DAQ
            while True:
                msg = await websocket.recv()
                try:
                    data = json.loads(msg)
                    if 'pressure' in data:
                        # Broadcast to all frontend clients
                        for client in list(frontend_clients):
                            try:
                                await client.send(json.dumps({'pressure': data['pressure']}))
                            except:
                                frontend_clients.discard(client)
                except Exception as e:
                    print(f"Error parsing DAQ message: {e}")
        else:
            # Treat as frontend client
            frontend_clients.add(websocket)
            print("Frontend client connected.")
            try:
                while True:
                    await asyncio.sleep(3600)  # Keep connection open
            finally:
                frontend_clients.discard(websocket)
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"Handler error: {e}")

async def main():
    async with websockets.serve(handler, HOST, PORT):
        print(f"Azure Pressure WebSocket server running on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main()) 