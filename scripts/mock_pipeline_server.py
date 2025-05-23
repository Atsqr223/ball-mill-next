# scripts/mock_pipeline_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import numpy as np
import time
import threading
import math
import pickle
import os

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

# Constants from the original implementation
PIPE_LENGTH_INTERVALS = 100  # Width of the heatmap
PIPE_DIAMETER_INTERVALS = 20  # Height of the heatmap
SAMPLING_RATE = 48000  # Hz
N_MICS = 4

# Global variables for heatmap simulation
latest_heatmap = None
heatmap_lock = threading.Lock()

def generate_heatmap():
    """Generate a simulated heatmap with dimensions matching the original implementation"""
    # Create base heatmap with correct dimensions
    heatmap = np.zeros((PIPE_DIAMETER_INTERVALS, PIPE_LENGTH_INTERVALS))
    
    # Current time for animation
    t = time.time()
    
    # Create a moving heat source
    center_x = int(PIPE_LENGTH_INTERVALS * (0.5 + 0.3 * math.sin(t)))
    center_y = int(PIPE_DIAMETER_INTERVALS * (0.5 + 0.3 * math.cos(t)))
    
    # Generate Gaussian heat distribution
    for y in range(PIPE_DIAMETER_INTERVALS):
        for x in range(PIPE_LENGTH_INTERVALS):
            # Calculate distance from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Create Gaussian heat distribution
            heat = math.exp(-(distance * distance) / 50)  # Adjusted for flatter distribution
            heatmap[y, x] = heat
    
    # Normalize to 0-1 range
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
    
    return heatmap.tolist()

def update_heatmap():
    """Background thread to continuously update the heatmap"""
    global latest_heatmap
    while True:
        try:
            new_heatmap = generate_heatmap()
            with heatmap_lock:
                latest_heatmap = new_heatmap
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")
        time.sleep(0.1)  # Update every 100ms

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

@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    with heatmap_lock:
        if latest_heatmap is None:
            return jsonify({'error': 'No heatmap data available'}), 503
        return jsonify({'heatmap': latest_heatmap})

if __name__ == '__main__':
    # Start the heatmap update thread
    update_thread = threading.Thread(target=update_heatmap, daemon=True)
    update_thread.start()
    
    logging.info("Starting mock pipeline server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
