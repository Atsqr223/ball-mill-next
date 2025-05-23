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
import nidaqmx
from nidaqmx import constants
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE, TerminalConfiguration
from nidaqmx import stream_readers

# Import the required functions from the original implementation
sys.path.append('pipe/N_MIC_LIVEDEMO_PLAYBACK')
from live_demo_dependencies.DOA_supporting_functions import *
from live_demo_dependencies.generate_bpfilt import *
from live_demo_dependencies.glob_vars import *
from live_demo_dependencies.doa_data_process import *
from live_demo_dependencies.BPF import *
from live_demo_dependencies.dmas import *

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
PIPE_LENGTH_INTERVALS = 50  # Width of the heatmap (from glob_vars.py)
PIPE_DIAMETER_INTERVALS = 5  # Height of the heatmap (from glob_vars.py)
SAMPLING_RATE = 48000  # Hz
N_MICS = 9  # Updated to 9 microphones
BAND_DISTANCE = 400  # Hz
FREQUENCY_FILTERING_ON = True

# Generate band-pass filter
fc, bw = generate_bpfilt_varyband(
    BAND_DISTANCE=BAND_DISTANCE,
    R_b=SAMPLING_RATE,
    lower_freq=1000,
    upper_freq=7000,
    tapered=True
)

# Global variables
latest_heatmap = None
heatmap_lock = threading.Lock()
audio_data = None
audio_lock = threading.Lock()
use_pickle = True  # Start with pickle mode by default

def normalize(data):
    """Normalize audio data as in the original implementation"""
    trace_mean = np.mean(data)
    data = [x-trace_mean for x in data]
    max_val = max(abs(min(data)), max(data))
    norm_trace = [x*4 for x in data]
    return norm_trace

def read_pickle_file():
    """Read audio data from pickle file"""
    try:
        with open('pickles/audio_file.pkl', 'rb') as f:
            data = pickle.load(f)
            if isinstance(data, int):  # Initial value in pickle
                logging.warning("Pickle file contains initial value, no audio data yet")
                return None
            if data.shape[1] != N_MICS:
                logging.warning(f"Pickle file has {data.shape[1]} channels, expected {N_MICS}")
            return data
    except FileNotFoundError:
        logging.error("Pickle file not found at pickles/audio_file.pkl")
        return None
    except Exception as e:
        logging.error(f"Error reading pickle file: {e}")
        return None

def try_nidaq_connection():
    """Try to establish connection with NI-DAQ"""
    try:
        with nidaqmx.Task() as task:
            logging.info("Attempting to connect to NI-DAQ device (Dev17)")
            task.ai_channels.add_ai_voltage_chan(
                f"Dev17/ai1:{N_MICS}",
                terminal_config=TerminalConfiguration.RSE
            )
            logging.info(f"Successfully configured {N_MICS} analog input channels")
            
            task.timing.cfg_samp_clk_timing(
                rate=SAMPLING_RATE,
                sample_mode=AcquisitionType.CONTINUOUS
            )
            logging.info(f"Successfully configured sampling rate: {SAMPLING_RATE} Hz")
            
            # Test reading a sample
            test_buffer = np.zeros((N_MICS, 1), dtype=np.float64)
            reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
            reader.read_many_sample(test_buffer, 1, timeout=1.0)
            logging.info("Successfully read test sample from NI-DAQ")
            
            return True
    except nidaqmx.errors.DaqError as e:
        logging.error(f"NI-DAQ error: {e}")
        if "Could not find an installation of NI-DAQmx" in str(e):
            logging.error("NI-DAQmx is not installed. Please install NI-DAQmx from National Instruments website.")
        elif "Device not found" in str(e):
            logging.error("NI-DAQ device (Dev17) not found. Please check connections.")
        elif "Channel not found" in str(e):
            logging.error(f"Channel configuration error. Check if {N_MICS} channels are available.")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during NI-DAQ connection: {e}")
        return False

def acquire_audio_data():
    """Acquire audio data from NI-DAQ or pickle file"""
    global audio_data, use_pickle
    
    # First try NI-DAQ
    if try_nidaq_connection():
        logging.info("Successfully connected to NI-DAQ")
        use_pickle = False
    else:
        logging.info("Falling back to pickle file mode")
        use_pickle = True
    
    while True:
        try:
            if use_pickle:
                # Read from pickle file
                data = read_pickle_file()
                if data is not None:
                    with audio_lock:
                        audio_data = data
                time.sleep(1)  # Update every second like original
            else:
                # Try to acquire from NI-DAQ
                with nidaqmx.Task() as task:
                    task.ai_channels.add_ai_voltage_chan(
                        f"Dev17/ai1:{N_MICS}",
                        terminal_config=TerminalConfiguration.RSE
                    )
                    task.timing.cfg_samp_clk_timing(
                        rate=SAMPLING_RATE,
                        sample_mode=AcquisitionType.CONTINUOUS
                    )
                    
                    in_stream = task.in_stream
                    reader = stream_readers.AnalogMultiChannelReader(in_stream)
                    
                    while True:
                        try:
                            # Acquire data
                            nSamples = 200
                            buffer = np.zeros((N_MICS, nSamples), dtype=np.float64)
                            reader.read_many_sample(buffer, nSamples, timeout=constants.WAIT_INFINITELY)
                            
                            # Process data
                            ch_data_list = []
                            for i in range(N_MICS):
                                ch_data_list.append(normalize(buffer[i]))
                            
                            # Update global audio data
                            with audio_lock:
                                audio_data = np.array(ch_data_list).T
                            
                            time.sleep(1)  # Update every second like original
                            
                        except Exception as e:
                            logging.error(f"Error acquiring audio data from NI-DAQ: {e}")
                            logging.info("Switching to pickle file mode")
                            use_pickle = True
                            break
                            
        except Exception as e:
            logging.error(f"Error in audio acquisition: {e}")
            time.sleep(1)

def generate_heatmap():
    """Generate heatmap from audio data using the MUSIC algorithm"""
    global audio_data, latest_heatmap
    
    while True:
        try:
            with audio_lock:
                if audio_data is None:
                    time.sleep(0.1)
                    continue
                
                current_data = audio_data.copy()
            
            # Process data using the original implementation's function
            p_music, sfreq_maps = data_process_pipe_animated_varyband_sfreqs(
                current_data,
                fc,
                bw,
                magType='linadd',
                theta_offset=180
            )
            
            # Normalize heatmap
            minval = np.min(p_music)
            maxval = np.max(p_music)
            p_music = (p_music - minval) / (maxval - minval)
            
            # Update global heatmap
            with heatmap_lock:
                latest_heatmap = p_music.T.tolist()
                
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")
        
        time.sleep(0.1)  # Update every 100ms

# Simulate GPIO control
class MockGPIO:
    def __init__(self):
        self.connected = False
        self.valve_states = [False, False, False]
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

@app.route('/mode', methods=['POST'])
def switch_mode():
    global use_pickle
    data = request.get_json()
    if not data or 'mode' not in data:
        return jsonify({'error': 'mode is required'}), 400
    
    mode = data['mode']
    if mode not in ['live', 'pickle']:
        return jsonify({'error': 'mode must be either "live" or "pickle"'}), 400
    
    if mode == 'live':
        if try_nidaq_connection():
            use_pickle = False
            logging.info("Switched to live mode with NI-DAQ")
            return jsonify({'status': 'success', 'mode': 'live'})
        else:
            logging.error("Failed to switch to live mode - NI-DAQ not available")
            return jsonify({'error': 'NI-DAQ not available'}), 503
    else:
        use_pickle = True
        logging.info("Switched to pickle mode")
        return jsonify({'status': 'success', 'mode': 'pickle'})

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
            'valveStates': valve_states,
            'mode': 'pickle' if use_pickle else 'live'
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
    # Start the audio acquisition thread
    audio_thread = threading.Thread(target=acquire_audio_data, daemon=True)
    audio_thread.start()
    
    # Start the heatmap generation thread
    heatmap_thread = threading.Thread(target=generate_heatmap, daemon=True)
    heatmap_thread.start()
    
    logging.info("Starting pipeline server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 
