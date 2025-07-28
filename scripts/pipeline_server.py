from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Store valve states
valve_states = [False, False, False]  # Store valve states
is_connected = True  # Always connected in this mode

def initialize_valves():
    """Initialize valves (no-op in this mode)"""
    global valve_states
    # Just return the current states without any hardware interaction
    return valve_states

def cleanup_gpio():
    """Clean up GPIO connections (no-op in this mode)"""
    return True

@app.route('/connect', methods=['POST'])
def connect():
    try:
        logger.info("Already connected in this mode")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/valve', methods=['POST'])
def control_valve():
    try:
        data = request.get_json()
        valve_index = data.get('valveIndex')
        state = data.get('state')
        
        if valve_index is None or state is None:
            logger.error("Missing valve index or state")
            return jsonify({'error': 'Valve index and state are required'}), 400
            
        if valve_index < 0 or valve_index >= len(valve_states):
            logger.error(f"Invalid valve index: {valve_index}")
            return jsonify({'error': 'Invalid valve index'}), 400
            
        # Update valve state in memory
        valve_states[valve_index] = state
            
        logger.info(f"Successfully set valve {valve_index} to {state}")
        return jsonify({
            'success': True,
            'valveStates': valve_states
        })
    except Exception as e:
        logger.error(f"Valve control error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    try:
        # Always return the current valve states regardless of connection status
        return jsonify({
            'connected': True,  # Always connected in this mode
            'valveStates': valve_states
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'connected': False,
            'valveStates': valve_states,
            'error': str(e)
        }), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
    try:
        global is_connected, factory, valves, valve_states
        if not is_connected:
            return jsonify({'success': True})

        # Reset valve states to default (all off)
        valve_states = [False, False, False]
        
        # Clean up GPIO connections
        if factory:
            for valve in valves:
                try:
                    valve.off()  # Ensure valves are turned off
                    valve.close()
                except Exception as e:
                    logger.error(f"Error closing valve: {str(e)}")
            valves = []
            factory = None
            is_connected = False

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Disconnect error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting pipeline control server...")
    app.run(host='0.0.0.0', port=5000)