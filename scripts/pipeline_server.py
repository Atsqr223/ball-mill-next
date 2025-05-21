from flask import Flask, request, jsonify
from flask_cors import CORS
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
import logging
import sys

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
        global factory
        factory = PiGPIOFactory(host=pi_ip)
        
        # Initialize valves
        global valves
        valves = [LED(pin, pin_factory=factory) for pin in VALVE_PINS]
        
        logger.info("Successfully connected to Raspberry Pi and initialized valves")
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
            
        if valve_index < 0 or valve_index >= len(VALVE_PINS):
            logger.error(f"Invalid valve index: {valve_index}")
            return jsonify({'error': 'Invalid valve index'}), 400
            
        if not valves:
            logger.error("Valves not initialized")
            return jsonify({'error': 'Not connected to Raspberry Pi'}), 400
            
        # Control valve
        valve = valves[valve_index]
        if state:
            logger.info(f"Opening valve {valve_index}")
            valve.on()
        else:
            logger.info(f"Closing valve {valve_index}")
            valve.off()
            
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Valve control error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    try:
        if not valves:
            return jsonify({
                'connected': False,
                'valveStates': [False, False, False]
            })
            
        return jsonify({
            'connected': True,
            'valveStates': [valve.is_lit for valve in valves]
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting pipeline control server...")
    app.run(host='0.0.0.0', port=5000) 