from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import time
import threading

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class MockGPIO:
    def __init__(self):
        self.pins = {
            22: False,  # Valve 1
            27: False,  # Valve 2
            17: False   # Valve 3
        }
        self.connected = False
        logging.info("Mock GPIO initialized")

    def connect(self):
        self.connected = True
        logging.info("Mock GPIO connected")
        return True

    def disconnect(self):
        # Turn off all pins
        for pin in self.pins:
            self.pins[pin] = False
        self.connected = False
        logging.info("Mock GPIO disconnected")
        return True

    def set_pin(self, pin, state):
        if pin in self.pins:
            self.pins[pin] = state
            logging.info(f"Pin {pin} set to {state}")
            return True
        return False

    def get_pin(self, pin):
        return self.pins.get(pin, None)

# Initialize mock GPIO
mock_gpio = MockGPIO()

@app.route('/connect', methods=['POST'])
def connect():
    logging.info("Received connection request")
    try:
        if mock_gpio.connect():
            return jsonify({'status': 'connected'})
        else:
            return jsonify({'error': 'Failed to connect'}), 500
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if mock_gpio.disconnect():
        return jsonify({'status': 'disconnected'})
    return jsonify({'error': 'Failed to disconnect'}), 500

@app.route('/valve', methods=['POST'])
def control_valve():
    logging.info("Received valve control request")
    if not mock_gpio.connected:
        logging.error("Attempted valve control without connection")
        return jsonify({'error': 'Not connected'}), 400

    data = request.get_json()
    if not data or 'valveIndex' not in data or 'state' not in data:
        logging.error("Valve control request missing required parameters")
        return jsonify({'error': 'valveIndex and state are required'}), 400

    valve_index = data['valveIndex']
    state = data['state']

    if not isinstance(valve_index, int) or valve_index < 0 or valve_index >= 3:
        logging.error(f"Invalid valve index: {valve_index}")
        return jsonify({'error': 'Invalid valve index'}), 400

    # Map valve index to GPIO pin
    pin_map = {
        0: 22,  # Valve 1 -> GPIO 22
        1: 27,  # Valve 2 -> GPIO 27
        2: 17   # Valve 3 -> GPIO 17
    }

    try:
        if mock_gpio.set_pin(pin_map[valve_index], state):
            return jsonify({'status': 'success', 'valveIndex': valve_index, 'state': state})
        else:
            return jsonify({'error': 'Failed to control valve'}), 500
    except Exception as e:
        logging.error(f"Valve control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    logging.info("Received status request")
    if not mock_gpio.connected:
        logging.error("Status request without connection")
        return jsonify({'error': 'Not connected'}), 400

    try:
        # Get states of all valves
        valve_states = [
            mock_gpio.get_pin(22),  # Valve 1
            mock_gpio.get_pin(27),  # Valve 2
            mock_gpio.get_pin(17)   # Valve 3
        ]
        logging.info(f"Current valve states: {valve_states}")
        return jsonify({
            'status': 'connected',
            'valveStates': valve_states
        })
    except Exception as e:
        logging.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting mock Raspberry Pi server on port 5003")
    app.run(host='0.0.0.0', port=5003, debug=True) 
