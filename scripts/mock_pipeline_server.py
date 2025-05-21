# scripts/mock_pipeline_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys

app = Flask(__name__)
CORS(app)

# Configure logging to show more visible output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Simulate GPIO control
class MockGPIO:
    def __init__(self):
        self.connected = False
        self.valve_states = [False, False, False]  # Simulate 3 valves
        logging.info("MockGPIO initialized with 3 valves")

    def connect(self, host):
        self.connected = True
        logging.info(f"MockGPIO connected to {host}")
        return True

    def disconnect(self):
        self.connected = False
        logging.info("MockGPIO disconnected")
        return True

    def set_valve(self, valve_index, state):
        if 0 <= valve_index < len(self.valve_states):
            self.valve_states[valve_index] = state
            logging.info(f"MockGPIO: Valve {valve_index} set to {state}")
            return True
        return False

    def get_valve_state(self, valve_index):
        if 0 <= valve_index < len(self.valve_states):
            return self.valve_states[valve_index]
        return None

# Initialize the mock GPIO
mock_gpio = MockGPIO()

@app.route('/connect', methods=['POST'])
def connect():
    logging.info("Received connection request")
    data = request.get_json()
    if not data or 'piIp' not in data:
        logging.error("Connection request missing IP address")
        return jsonify({'error': 'IP address is required'}), 400

    try:
        if mock_gpio.connect(data['piIp']):
            logging.info(f"Connected to mock Raspberry Pi at {data['piIp']}")
            return jsonify({'status': 'connected'})
        else:
            logging.error("Failed to connect to mock Raspberry Pi")
            return jsonify({'error': 'Failed to connect'}), 500
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/valve', methods=['POST'])
def control_valve():
    logging.info("Received valve control request")
    if not mock_gpio.connected:
        logging.error("Attempted valve control without connection")
        return jsonify({'error': 'Not connected to Raspberry Pi'}), 400

    data = request.get_json()
    if not data or 'valveIndex' not in data or 'state' not in data:
        logging.error("Valve control request missing required parameters")
        return jsonify({'error': 'valveIndex and state are required'}), 400

    valve_index = data['valveIndex']
    state = data['state']

    if not isinstance(valve_index, int) or valve_index < 0 or valve_index >= 3:
        logging.error(f"Invalid valve index: {valve_index}")
        return jsonify({'error': 'Invalid valve index'}), 400

    try:
        if mock_gpio.set_valve(valve_index, state):
            logging.info(f"Valve {valve_index} set to {state}")
            return jsonify({'status': 'success'})
        else:
            logging.error(f"Failed to control valve {valve_index}")
            return jsonify({'error': 'Failed to control valve'}), 500
    except Exception as e:
        logging.error(f"Valve control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    logging.info("Received status request")
    if not mock_gpio.connected:
        logging.error("Status request without connection")
        return jsonify({'error': 'Not connected to Raspberry Pi'}), 400

    try:
        valve_states = [mock_gpio.get_valve_state(i) for i in range(3)]
        logging.info(f"Current valve states: {valve_states}")
        return jsonify({
            'status': 'connected',
            'valveStates': valve_states
        })
    except Exception as e:
        logging.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting mock pipeline server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)