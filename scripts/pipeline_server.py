from flask import Flask, request, jsonify
from flask_cors import CORS
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
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

# Store GPIO pins for each valve
VALVE_PINS = [22, 27, 17]  # Same pins as in the original script
valves = []
factory = None
is_connected = False

def initialize_valves():
    """Initialize or reinitialize all valves"""
    global valves, factory
    try:
        if factory:
            # Clean up existing valves
            for valve in valves:
                try:
                    valve.off()
                except:
                    pass
            valves = []
        
        # Create new valve instances
        valves = [LED(pin, pin_factory=factory) for pin in VALVE_PINS]
        # Ensure all valves start in the off position
        for valve in valves:
            valve.off()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize valves: {str(e)}")
        return False

@app.route('/connect', methods=['POST'])
def connect():
    try:
        data = request.get_json()
        pi_ip = data.get('piIp')
        
        if not pi_ip:
            logger.error("No IP address provided")
            return jsonify({'error': 'Raspberry Pi IP address is required'}), 400
            
        logger.info(f"Attempting to connect to Raspberry Pi at {pi_ip}")
        
        # Create factory instance
        global factory, is_connected
        try:
            factory = PiGPIOFactory(host=pi_ip)
            # Test connection by trying to initialize valves
            if not initialize_valves():
                raise Exception("Failed to initialize valves")
            is_connected = True
            logger.info("Successfully connected to Raspberry Pi and initialized valves")
            return jsonify({'success': True})
        except Exception as e:
            factory = None
            is_connected = False
            raise e
            
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/valve', methods=['POST'])
def control_valve():
    try:
        if not is_connected or not valves:
            logger.error("Not connected to Raspberry Pi")
            return jsonify({'error': 'Not connected to Raspberry Pi'}), 400

        data = request.get_json()
        valve_index = data.get('valveIndex')
        state = data.get('state')
        
        if valve_index is None or state is None:
            logger.error("Missing valve index or state")
            return jsonify({'error': 'Valve index and state are required'}), 400
            
        if valve_index < 0 or valve_index >= len(VALVE_PINS):
            logger.error(f"Invalid valve index: {valve_index}")
            return jsonify({'error': 'Invalid valve index'}), 400
            
        # Control valve with retry logic
        max_retries = 3
        retry_delay = 0.1  # seconds
        
        for attempt in range(max_retries):
            try:
                valve = valves[valve_index]
                if state:
                    logger.info(f"Opening valve {valve_index}")
                    valve.on()
                else:
                    logger.info(f"Closing valve {valve_index}")
                    valve.off()
                
                # Verify the valve state
                time.sleep(retry_delay)  # Give the valve time to respond
                if valve.is_lit == state:
                    return jsonify({'success': True})
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Valve state mismatch, retrying... (attempt {attempt + 1}/{max_retries})")
                        continue
                    else:
                        raise Exception("Failed to set valve state after multiple attempts")
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Valve control error, retrying... (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise e
                    
    except Exception as e:
        logger.error(f"Valve control error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    try:
        if not is_connected or not valves:
            return jsonify({
                'connected': False,
                'valveStates': [False, False, False]
            })
            
        # Get current valve states
        valve_states = []
        for valve in valves:
            try:
                valve_states.append(valve.is_lit)
            except:
                # If we can't read a valve's state, assume it's off
                valve_states.append(False)
                
        return jsonify({
            'connected': True,
            'valveStates': valve_states
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'connected': False,
            'valveStates': [False, False, False],
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting pipeline control server...")
    app.run(host='0.0.0.0', port=5000) 