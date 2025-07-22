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
lower_pressure_threshold = None # New lower threshold
current_pressure = None
compressor_on = False
pressure_lock = threading.Lock()
valve_states = [False, False, False] # Assuming 3 valves, initially OFF

# Toggle-range mode state
toggle_range_active = False
toggle_range_valve = None
toggle_range_phase = None # 'compressing' or 'releasing'

# --- Pressure Monitoring Thread (HTTP Polling) ---
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

# --- Pressure Monitoring Thread (HTTP Polling) ---
def pressure_poll_thread():
    global current_pressure, compressor_on, pressure_threshold, lower_pressure_threshold, toggle_range_active, toggle_range_phase, toggle_range_valve
    while True:
        try:
            resp = requests.get(PRESSURE_HTTP_URL, timeout=2)
            if resp.ok:
                data = resp.json()
                pressure = data.get('pressure')
                if pressure is not None:
                    with pressure_lock:
                        current_pressure = pressure

                        # --- Toggle Range Mode Logic ---
                        if toggle_range_active:
                            # Phase 1: Compressing
                            if toggle_range_phase == 'compressing' and pressure_threshold is not None and current_pressure >= pressure_threshold:
                                print("[TOGGLE-RANGE] Reached upper threshold. Switching to release phase.")
                                set_compressor_state(False)
                                set_valve_state(toggle_range_valve, True)
                                toggle_range_phase = 'releasing'
                            
                            # Phase 2: Releasing
                            elif toggle_range_phase == 'releasing' and lower_pressure_threshold is not None and current_pressure <= lower_pressure_threshold:
                                print("[TOGGLE-RANGE] Reached lower threshold. Switching to compress phase.")
                                set_valve_state(toggle_range_valve, False)
                                set_compressor_state(True)
                                toggle_range_phase = 'compressing'
                            
                            continue # Skip normal checks when in toggle mode

                        # --- Normal Operation Logic (runs if toggle mode is OFF) ---
                        
                        # Auto-switch off compressor if upper threshold is set and reached
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
                        
                        # Auto-switch off all valves if lower threshold is set, pressure is low, and any valve is on
                        if (
                            lower_pressure_threshold is not None and
                            any(valve_states) and # Only trigger if at least one valve is on
                            pressure <= lower_pressure_threshold
                        ):
                            turn_off_all_valves()
                            print(f"[AUTO] Lower pressure threshold event handled. All valves turned off.")
        except Exception as e:
            print(f"[HTTP] Error polling pressure: {e}")
        time.sleep(1)

# --- REST API ---
@app.route('/valve', methods=['POST'])
def control_valve():
    data = request.get_json()
    global valve_states
    valve_index = data.get('valveIndex')
    state = data.get('state')
    if valve_index is None or state is None:
        return jsonify({'error': 'valveIndex and state required'}), 400
    if set_valve_state(valve_index, bool(state)):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to set valve state'}), 500

@app.route('/compressor', methods=['POST'])
def control_compressor():
    global compressor_on
    data = request.get_json()
    value = data.get('value')
    if value is None:
        return jsonify({'error': 'value required'}), 400
    if set_compressor_state(bool(value)):
        return jsonify({'success': True})
    else:
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
def set_lower_pressure_threshold():
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
def get_lower_pressure_threshold():
    return jsonify({'lower_threshold': lower_pressure_threshold})

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
            'lower_threshold': lower_pressure_threshold,
            'compressor_on': compressor_on,
            'valve_states': valve_states,
            'toggle_range_mode': {
                'active': toggle_range_active,
                'valve': toggle_range_valve,
                'phase': toggle_range_phase
            }
        })

@app.route('/toggle-range', methods=['POST'])
def toggle_range_mode():
    global toggle_range_active, toggle_range_valve, toggle_range_phase
    data = request.get_json()
    state = data.get('state')

    if state == 'on':
        valve_index = data.get('valveIndex')
        if valve_index is None:
            return jsonify({'error': 'valveIndex required to start toggle-range mode'}), 400
        if pressure_threshold is None or lower_pressure_threshold is None:
            return jsonify({'error': 'Upper and lower thresholds must be set before starting toggle-range mode'}), 400
        
        toggle_range_active = True
        toggle_range_valve = valve_index
        toggle_range_phase = 'compressing' # Start by compressing
        
        # Initial state
        set_compressor_state(True)
        for i in range(len(valve_states)):
            if i != toggle_range_valve:
                set_valve_state(i, False)

        print(f"[MODE] Toggle-range mode STARTED for valve {toggle_range_valve}")
        return jsonify({'success': True, 'message': f'Toggle-range mode started for valve {valve_index}'})
    
    elif state == 'off':
        if not toggle_range_active:
            return jsonify({'success': True, 'message': 'Toggle-range mode was not active.'})

        print("[MODE] Toggle-range mode STOPPED")
        set_compressor_state(False)
        if toggle_range_valve is not None:
            set_valve_state(toggle_range_valve, False)

        toggle_range_active = False
        toggle_range_valve = None
        toggle_range_phase = None
        return jsonify({'success': True, 'message': 'Toggle-range mode stopped'})

    else:
        return jsonify({'error': 'Invalid state. Must be "on" or "off"'}), 400

if __name__ == '__main__':
    # Start pressure polling thread
    t = threading.Thread(target=pressure_poll_thread, daemon=True)
    t.start()
    print(f"[INFO] Control server running on port {CONTROL_SERVER_PORT}...")
    app.run(host='0.0.0.0', port=CONTROL_SERVER_PORT) 