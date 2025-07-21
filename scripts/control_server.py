import threading
import time
import requests
import json
from flask import Flask, request, jsonify, Response
import websocket

app = Flask(__name__)

# Configurable
VALVE_API_URL = 'http://localhost:3000/api/pipeline/valve'  # Next.js API
COMPRESSOR_API_URL = 'http://localhost:3000/api/pipeline/plc-io'
PRESSURE_WS_URL = 'ws://localhost:65506'

# State
pressure_threshold = None
current_pressure = None
compressor_on = False
pressure_lock = threading.Lock()

# Store last used Raspberry Pi IP
last_pi_ip = None

# --- Pressure Monitoring Thread ---
def pressure_ws_thread():
    global current_pressure, compressor_on, pressure_threshold
    def on_message(ws, message):
        global current_pressure, compressor_on, pressure_threshold
        try:
            data = json.loads(message)
            pressure = data.get('pressure')
            if pressure is not None:
                with pressure_lock:
                    current_pressure = pressure
                    # Auto-switch off compressor if threshold is set and reached
                    if (
                        pressure_threshold is not None and
                        compressor_on and
                        pressure >= pressure_threshold
                    ):
                        # Turn off compressor
                        try:
                            resp = requests.post(COMPRESSOR_API_URL, json={'value': False})
                            if resp.ok:
                                compressor_on = False
                                print(f"[AUTO] Compressor turned OFF at pressure {pressure}")
                        except Exception as e:
                            print(f"[AUTO] Error turning off compressor: {e}")
        except Exception as e:
            print(f"[WS] Error parsing message: {e}")

    def on_error(ws, error):
        print(f"[WS] Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("[WS] Connection closed. Reconnecting in 3s...")
        time.sleep(3)
        start_ws_thread()

    def on_open(ws):
        print("[WS] Connected to pressure WebSocket.")

    def start_ws_thread():
        ws = websocket.WebSocketApp(
            PRESSURE_WS_URL,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        ws.run_forever()

    start_ws_thread()

# --- REST API ---
@app.route('/valve', methods=['POST'])
def control_valve():
    data = request.get_json()
    valve_index = data.get('valveIndex')
    state = data.get('state')
    if valve_index is None or state is None:
        return jsonify({'error': 'valveIndex and state required'}), 400
    try:
        resp = requests.post(VALVE_API_URL, json={'valveIndex': valve_index, 'state': state})
        excluded_headers = ['content-encoding', 'transfer-encoding', 'content-length', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compressor', methods=['POST'])
def control_compressor():
    global compressor_on
    data = request.get_json()
    value = data.get('value')
    if value is None:
        return jsonify({'error': 'value required'}), 400
    try:
        resp = requests.post(COMPRESSOR_API_URL, json={'value': value})
        if resp.ok:
            compressor_on = bool(value)
        excluded_headers = ['content-encoding', 'transfer-encoding', 'content-length', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pressure-threshold', methods=['POST'])
def set_pressure_threshold():
    global pressure_threshold
    data = request.get_json()
    threshold = data.get('threshold')
    if threshold is None:
        return jsonify({'error': 'threshold required'}), 400
    try:
        pressure_threshold = float(threshold)
        return jsonify({'success': True, 'threshold': pressure_threshold})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/pressure-threshold', methods=['GET'])
def get_pressure_threshold():
    return jsonify({'threshold': pressure_threshold})

@app.route('/pressure', methods=['GET'])
def get_pressure():
    with pressure_lock:
        return jsonify({'pressure': current_pressure})

@app.route('/status', methods=['GET'])
def get_status():
    with pressure_lock:
        return jsonify({
            'pressure': current_pressure,
            'threshold': pressure_threshold,
            'compressor_on': compressor_on
        })

@app.route('/connect-pi', methods=['POST'])
def connect_pi():
    global last_pi_ip
    data = request.get_json()
    pi_ip = data.get('piIp')
    if not pi_ip:
        return jsonify({'error': 'piIp required'}), 400
    try:
        # Forward the connection request to the pipeline server
        resp = requests.post('http://localhost:3000/api/pipeline/connect', json={'piIp': pi_ip})
        last_pi_ip = pi_ip
        excluded_headers = ['content-encoding', 'transfer-encoding', 'content-length', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start pressure monitoring thread
    t = threading.Thread(target=pressure_ws_thread, daemon=True)
    t.start()
    print("[INFO] Control server running on port 65507...")
    app.run(host='0.0.0.0', port=65507) 