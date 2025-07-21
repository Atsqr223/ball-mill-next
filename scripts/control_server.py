import threading
import time
import requests
import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Use existing environment variables
WEB_HOST = os.environ.get('NEXT_PUBLIC_WEB_HOST', 'localhost')
WEB_PORT = os.environ.get('PORT', '65500')
CONTROL_SERVER_PORT = int(os.environ.get('CONTROL_SERVER_PORT', '65508'))
PRESSURE_HTTP_URL = os.environ.get('PRESSURE_HTTP_URL', 'http://localhost:65507/latest_pressure')

# Configurable URLs
VALVE_API_URL = f'http://{WEB_HOST}:{WEB_PORT}/api/pipeline/valve'
COMPRESSOR_API_URL = f'http://{WEB_HOST}:{WEB_PORT}/api/pipeline/plc-io'

# State
pressure_threshold = None
current_pressure = None
compressor_on = False
pressure_lock = threading.Lock()

# --- Pressure Monitoring Thread (HTTP Polling) ---
def pressure_poll_thread():
    global current_pressure, compressor_on, pressure_threshold
    while True:
        try:
            resp = requests.get(PRESSURE_HTTP_URL, timeout=2)
            if resp.ok:
                data = resp.json()
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
                            try:
                                r = requests.post(COMPRESSOR_API_URL, json={'value': False})
                                if r.ok:
                                    compressor_on = False
                                    print(f"[AUTO] Compressor turned OFF at pressure {pressure}")
                            except Exception as e:
                                print(f"[AUTO] Error turning off compressor: {e}")
        except Exception as e:
            print(f"[HTTP] Error polling pressure: {e}")
        time.sleep(1)

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
        return jsonify(resp.json()), resp.status_code
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
        return jsonify(resp.json()), resp.status_code
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

if __name__ == '__main__':
    # Start pressure polling thread
    t = threading.Thread(target=pressure_poll_thread, daemon=True)
    t.start()
    print(f"[INFO] Control server running on port {CONTROL_SERVER_PORT}...")
    app.run(host='0.0.0.0', port=CONTROL_SERVER_PORT) 