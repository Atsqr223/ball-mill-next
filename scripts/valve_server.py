from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

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

class ValveController:
    def __init__(self):
        self.connected = False
        self.factory = None
        self.leds = None
        self.button_pins = [22, 27, 17]  # GPIO pins for valves
        logging.info("Valve controller initialized")

    def connect(self, pi_ip):
        try:
            self.factory = PiGPIOFactory(host=pi_ip)
            self.leds = [LED(pin, pin_factory=self.factory) for pin in self.button_pins]
            self.connected = True
            logging.info(f"Connected to Raspberry Pi at {pi_ip}")
            return True
        except Exception as e:
            logging.error(f"Error connecting to Raspberry Pi: {e}")
            return False

    def disconnect(self):
        try:
            if self.leds:
                for led in self.leds:
                    led.off()
                self.leds = None
            self.factory = None
            self.connected = False
            logging.info("Disconnected from Raspberry Pi")
            return True
        except Exception as e:
            logging.error(f"Error disconnecting from Raspberry Pi: {e}")
            return False

    def set_valve(self, valve_index, state):
        if not self.connected or not self.leds:
            return False
        try:
            if 0 <= valve_index < len(self.leds):
                if state:
                    self.leds[valve_index].on()
                else:
                    self.leds[valve_index].off()
                logging.info(f"Valve {valve_index} set to {state}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error setting valve: {e}")
            return False

    def get_valve_state(self, valve_index):
        if not self.connected or not self.leds:
            return None
        try:
            if 0 <= valve_index < len(self.leds):
                return self.leds[valve_index].is_lit
            return None
        except Exception as e:
            logging.error(f"Error getting valve state: {e}")
            return None

# Initialize the valve controller
valve_controller = ValveController()

@app.route('/connect', methods=['POST'])
def connect():
    logging.info("Received connection request")
    data = request.get_json()
    if not data or 'piIp' not in data:
        logging.error("Connection request missing IP address")
        return jsonify({'error': 'IP address is required'}), 400

    try:
        if valve_controller.connect(data['piIp']):
            return jsonify({'status': 'connected'})
        else:
            return jsonify({'error': 'Failed to connect to Raspberry Pi'}), 500
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if valve_controller.disconnect():
        return jsonify({'status': 'disconnected'})
    return jsonify({'error': 'Failed to disconnect from Raspberry Pi'}), 500

@app.route('/valve', methods=['POST'])
def control_valve():
    logging.info("Received valve control request")
    if not valve_controller.connected:
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
        if valve_controller.set_valve(valve_index, state):
            return jsonify({'status': 'success', 'valveIndex': valve_index, 'state': state})
        else:
            return jsonify({'error': 'Failed to control valve on Raspberry Pi'}), 500
    except Exception as e:
        logging.error(f"Valve control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    logging.info("Received status request")
    if not valve_controller.connected:
        logging.error("Status request without connection")
        return jsonify({'error': 'Not connected to Raspberry Pi'}), 400

    try:
        valve_states = [valve_controller.get_valve_state(i) for i in range(3)]
        logging.info(f"Current valve states: {valve_states}")
        return jsonify({
            'status': 'connected',
            'valveStates': valve_states
        })
    except Exception as e:
        logging.error(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting valve control server on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True) 
