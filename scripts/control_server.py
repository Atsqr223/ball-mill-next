import threading
import time
import requests
import json
from flask import Flask, request, jsonify, Response
import websocket
import random

app = Flask(__name__)

# Configurable
VALVE_API_URL = 'http://localhost:3000/api/pipeline/valve'
COMPRESSOR_API_URL = 'http://localhost:3000/api/pipeline/plc-io'
PRESSURE_WS_URL = 'ws://localhost:65506'

# State
pressure_threshold = None
lower_pressure_threshold = None
current_pressure = None
compressor_on = False
pressure_lock = threading.Lock()
valve_states = [False, False, False]

# Toggle-range mode
toggle_range_active = False
toggle_range_valve = None
toggle_range_phase = None  # 'compressing' or 'releasing'

def set_compressor_state(state):
    global compressor_on
    try:
        r = requests.post(COMPRESSOR_API_URL, json={'value': state})
        if r.ok:
            compressor_on = state
            print(f"[CMD] Compressor turned {'ON' if state else 'OFF'}")
            return True
    except Exception as e:
        print(f"[CMD] Error setting compressor state: {e}")
    return False

def set_valve_state(valve_index, state):
    global valve_states
    try:
        r = requests.post(VALVE_API_URL, json={'valveIndex': valve_index, 'state': state})
        if r.ok:
            if 0 <= valve_index < len(valve_states):
                valve_states[valve_index] = state
            print(f"[CMD] Valve {valve_index} turned {'ON' if state else 'OFF'}")
            return True
    except Exception as e:
        print(f"[CMD] Error setting valve {valve_index} state: {e}")
    return False

def turn_off_all_valves():
    print("[AUTO] Turning off all valves due to low pressure.")
    for i in range(3):
        set_valve_state(i, False)

def pressure_ws_thread():
    def on_message(ws, message):
        global current_pressure, compressor_on, pressure_threshold, lower_pressure_threshold
        global toggle_range_active, toggle_range_phase, toggle_range_valve

        try:
            data = json.loads(message)
            pressure = data.get('pressure')
            if pressure is not None:
                with pressure_lock:
                    current_pressure = pressure

                    if toggle_range_active:
                        if toggle_range_phase == 'compressing' and pressure_threshold is not None and pressure >= pressure_threshold:
                            print("[TOGGLE-RANGE] Reached upper threshold. Releasing pressure.")
                            set_compressor_state(False)
                            set_valve_state(toggle_range_valve, True)
                            toggle_range_phase = 'releasing'

                        elif toggle_range_phase == 'releasing' and lower_pressure_threshold is not None and pressure <= lower_pressure_threshold:
                            print("[TOGGLE-RANGE] Reached lower threshold. Compressing.")
                            set_valve_state(toggle_range_valve, False)
                            set_compressor_state(True)
                            toggle_range_phase = 'compressing'
                        return  # Skip normal mode

                    if pressure_threshold is not None and compressor_on and pressure >= pressure_threshold:
                        set_compressor_state(False)
                        print(f"[AUTO] Compressor turned OFF at pressure {pressure}")

                    if lower_pressure_threshold is not None and any(valve_states) and pressure <= lower_pressure_threshold:
                        turn_off_all_valves()
                        print(f"[AUTO] Lower pressure threshold event handled. All valves turned off.")

        except Exception as e:
            print(f"[WS] Error parsing message: {e}")

    def on_error(ws, error):
        print(f"[WS] Error: {error}")

    def on_close(ws, code, msg):
        print("[WS] Closed. Reconnecting in 3s...")
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

# --- Flask Endpoints ---
@app.route('/valve', methods=['POST'])
def control_valve():
    data = request.get_json()
    valve_index = data.get('valveIndex')
    state = data.get('state')
    if valve_index is None or state is None:
        return jsonify({'error': 'valveIndex and state required'}), 400
    if set_valve_state(valve_index, bool(state)):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to set valve state'}), 500

@app.route('/compressor', methods=['POST'])
def control_compressor():
    data = request.get_json()
    value = data.get('value')
    if value is None:
        return jsonify({'error': 'value required'}), 400
    if set_compressor_state(bool(value)):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to set compressor state'}), 500

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

@app.route('/lower-pressure-threshold', methods=['POST'])
def set_lower_threshold():
    global lower_pressure_threshold
    data = request.get_json()
    threshold = data.get('threshold')
    if threshold is None:
        return jsonify({'error': 'threshold required'}), 400
    try:
        lower_pressure_threshold = float(threshold)
        return jsonify({'success': True, 'lower_threshold': lower_pressure_threshold})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/lower-pressure-threshold', methods=['GET'])
def get_lower_threshold():
    return jsonify({'lower_threshold': lower_pressure_threshold})

@app.route('/toggle-range', methods=['POST'])
def toggle_range_mode():
    global toggle_range_active, toggle_range_valve, toggle_range_phase
    data = request.get_json()
    state = data.get('state')

    if state == 'on':
        valve_index = data.get('valveIndex')
        if valve_index is None:
            valve_index = random.choice([0, 1, 2])
            print(f"[MODE] Randomly selected valve {valve_index}")
        if pressure_threshold is None or lower_pressure_threshold is None:
            return jsonify({'error': 'Both thresholds must be set first'}), 400

        toggle_range_active = True
        toggle_range_valve = valve_index
        toggle_range_phase = 'compressing'
        set_compressor_state(True)
        for i in range(3):
            if i != valve_index:
                set_valve_state(i, False)
        print(f"[MODE] Toggle-range mode STARTED on valve {valve_index}")
        return jsonify({'success': True, 'message': f'Toggle-range started on valve {valve_index}'})

    elif state == 'off':
        if toggle_range_valve is not None:
            set_valve_state(toggle_range_valve, False)
        set_compressor_state(False)
        toggle_range_active = False
        toggle_range_valve = None
        toggle_range_phase = None
        print("[MODE] Toggle-range mode STOPPED")
        return jsonify({'success': True, 'message': 'Toggle-range stopped'})

    return jsonify({'error': 'Invalid state'}), 400

@app.route('/status', methods=['GET'])
def get_status():
    with pressure_lock:
        return jsonify({
            'pressure': current_pressure,
            'threshold': pressure_threshold,
            'lower_threshold': lower_pressure_threshold,
            'compressor_on': compressor_on,
            'valve_states': valve_states,
            'toggle_range_mode': {
                'active': toggle_range_active,
                'valve': toggle_range_valve,
                'phase': toggle_range_phase
            }
        })

@app.route('/connect-pi', methods=['POST'])
def connect_pi():
    global last_pi_ip
    data = request.get_json()
    pi_ip = data.get('piIp')
    if not pi_ip:
        return jsonify({'error': 'piIp required'}), 400
    try:
        resp = requests.post('http://localhost:3000/api/pipeline/connect', json={'piIp': pi_ip})
        last_pi_ip = pi_ip
        excluded_headers = ['content-encoding', 'transfer-encoding', 'content-length', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    t = threading.Thread(target=pressure_ws_thread, daemon=True)
    t.start()
    print("[INFO] Control server running on port 65508..")
    app.run(host='0.0.0.0', port=65508)
