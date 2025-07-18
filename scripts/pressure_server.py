import asyncio
import websockets
import json
import threading
from flask import Flask, jsonify
from flask_cors import CORS

HOST = '0.0.0.0'
WS_PORT = 65506
HTTP_PORT = 65507

latest_pressure = None

# Flask app for HTTP API
app = Flask(__name__)
CORS(app)

@app.route('/latest_pressure')
def get_latest_pressure():
    if latest_pressure is not None:
        return jsonify({'pressure': latest_pressure})
    else:
        return jsonify({'pressure': None}), 404

def run_flask():
    app.run(host=HOST, port=HTTP_PORT)

# WebSocket server
daq_client = None
frontend_clients = set()

async def handler(websocket, path):
    global daq_client, latest_pressure
    try:
        reg_msg = await websocket.recv()
        reg_data = json.loads(reg_msg)
        if reg_data.get('type') == 'registerDAQ':
            daq_client = websocket
            print("DAQ client connected.")
            while True:
                msg = await websocket.recv()
                try:
                    data = json.loads(msg)
                    if 'pressure' in data:
                        latest_pressure = data['pressure']
                        # (Optional) broadcast to frontend clients if you want
                except Exception as e:
                    print(f"Error parsing DAQ message: {e}")
        else:
            # Frontend clients can just connect and do nothing
            print("Frontend client connected.")
            try:
                while True:
                    await asyncio.sleep(3600)
            finally:
                pass
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"Handler error: {e}")

async def main():
    ws_server = websockets.serve(handler, HOST, WS_PORT)
    await ws_server
    print(f"Azure Pressure WebSocket server running on ws://{HOST}:{WS_PORT}")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # Start WebSocket server
    asyncio.run(main()) 