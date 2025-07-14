import time
import requests
import snap7
from snap7.util import set_bool
import snap7.type
import logging
import signal
import sys

# --- Configuration ---
AZURE_PLC_STATUS_URL = 'http://<azure_ip>:65504/status'  # <-- Replace with your Azure VM's public IP or DNS
PLC_IP = '10.135.114.201'  # Siemens PLC IP
RACK = 0
SLOT = 1
POLL_INTERVAL = 2  # seconds

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# --- PLC setup ---
try:
    plc = snap7.client.Client()
    plc.connect(PLC_IP, RACK, SLOT)
    logging.info(f"Connected to PLC at {PLC_IP}")
except Exception as e:
    logging.error(f"Failed to connect to PLC: {e}")
    sys.exit(1)

def write_m0_0(value):
    byte_index = 0
    bit_index = 0
    data = plc.read_area(snap7.type.Areas.MK, 0, byte_index, 1)
    set_bool(data, 0, bit_index, value)
    plc.write_area(snap7.type.Areas.MK, 0, byte_index, data)

last_state = None

def cleanup():
    logging.info("Disconnecting from PLC...")
    try:
        plc.disconnect()
    except Exception:
        pass

def signal_handler(sig, frame):
    cleanup()
    logging.info("Exiting PLC poller.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# --- Main polling loop ---
while True:
    try:
        resp = requests.get(AZURE_PLC_STATUS_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        compressor_state = data.get('compressor')
        if compressor_state is None:
            logging.warning(f"Invalid response: {data}")
            time.sleep(POLL_INTERVAL)
            continue

        if last_state != compressor_state:
            write_m0_0(compressor_state)
            logging.info(f"Set PLC compressor (M0.0) to: {compressor_state}")
            last_state = compressor_state
    except Exception as e:
        logging.error(f"Polling or PLC error: {e}")
    time.sleep(POLL_INTERVAL)