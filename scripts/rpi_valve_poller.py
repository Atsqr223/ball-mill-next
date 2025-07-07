import time
import requests
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
import logging

# --- Configuration ---
AZURE_STATUS_URL = 'http://azure_ip:65501/status'  # <-- Replace with your Azure VM's public IP or DNS
VALVE_PINS = [22, 27, 17]  # GPIO pins for the valves
POLL_INTERVAL = 1 # seconds

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# --- GPIO setup ---
try:
    factory = PiGPIOFactory()  # Local pigpio daemon
    valves = [LED(pin, pin_factory=factory) for pin in VALVE_PINS]
    logging.info(f"Initialized valves on pins: {VALVE_PINS}")
except Exception as e:
    logging.error(f"Failed to initialize GPIO: {e}")
    exit(1)

# --- State tracking ---
last_states = [None] * len(VALVE_PINS)

# --- Main polling loop ---
while True:
    try:
        resp = requests.get(AZURE_STATUS_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        valve_states = data.get('valveStates')
        if not isinstance(valve_states, list) or len(valve_states) != len(VALVE_PINS):
            logging.warning(f"Invalid valveStates in response: {valve_states}")
            time.sleep(POLL_INTERVAL)
            continue

        # Set each valve to the desired state
        for i, (valve, desired) in enumerate(zip(valves, valve_states)):
            if last_states[i] != desired:
                if desired:
                    valve.on()
                    logging.info(f"Valve {i} (GPIO {VALVE_PINS[i]}) ON")
                else:
                    valve.off()
                    logging.info(f"Valve {i} (GPIO {VALVE_PINS[i]}) OFF")
                last_states[i] = desired
    except Exception as e:
        logging.error(f"Polling error: {e}")
    time.sleep(POLL_INTERVAL) 