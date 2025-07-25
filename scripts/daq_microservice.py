import sys
import os
import numpy as np
import time
import threading
import queue
from flask import Flask, jsonify
import nidaqmx
from nidaqmx import stream_readers
from nidaqmx.constants import TerminalConfiguration
import scipy.signal as sp
from dotenv import load_dotenv
load_dotenv()

# Add pipeline path for imports
base_dir = os.path.dirname(os.path.abspath(__file__))
pipe_path = os.path.abspath(os.path.join(base_dir, '..', 'pipe'))
sys.path.append(pipe_path)

# Import the real heatmap function and globals
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.doa_data_process import data_process_pipe_animated_varyband_sfreqs
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.glob_vars import SAMPLING_RATE, THETA_OFFSET, PIPE_LENGTH_INTERVALS, PIPE_DIAMETER_INTERVALS
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.generate_bpfilt import generate_bpfilt_varyband

# Config
CHANNELS = 9
BUFFER_SIZE = SAMPLING_RATE  # 1 second buffer
BAND_DISTANCE = 400
LOWER_FREQ = 1000
UPPER_FREQ = 7000
FILTER_ORDER = 5
FILTER_PADDING = 100
AUDIO_SIZE_REDUCTION_FACTOR = 4

# Globals
ch_data_list = np.array([np.zeros(BUFFER_SIZE) for _ in range(CHANNELS)])
data_queue = queue.Queue(maxsize=500)
heatmap_data = None
last_update_time = 0

fc, bw = generate_bpfilt_varyband(BAND_DISTANCE, SAMPLING_RATE, LOWER_FREQ, UPPER_FREQ)
butter_b, butter_a = sp.butter(FILTER_ORDER, [LOWER_FREQ, UPPER_FREQ], btype='band', fs=SAMPLING_RATE)

def setup_task():
    try:
        t = nidaqmx.Task()
        t.ai_channels.add_ai_voltage_chan(f"Dev1/ai1:{CHANNELS}", terminal_config=TerminalConfiguration.RSE)
        t.timing.cfg_samp_clk_timing(
            rate=SAMPLING_RATE,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=BUFFER_SIZE
        )
        in_stream = t.in_stream
        reader = stream_readers.AnalogMultiChannelReader(in_stream)
        return t, reader
    except Exception as e:
        print(f"Failed to set up NI-DAQ task: {e}")
        return None, None

def acquire_data():
    global ch_data_list
    task, reader = setup_task()
    if not task or not reader:
        print("DAQ task or reader not initialized.")
        return
    try:
        while True:
            try:
                reader.read_many_sample(
                    data=ch_data_list,
                    number_of_samples_per_channel=BUFFER_SIZE
                )
                data = np.array(ch_data_list).T
                if len(data.shape) == 1:
                    data = data.reshape(-1, 1)
                data_queue.put(data)
            except Exception as e:
                print(f"Error acquiring data: {str(e)}")
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received - shutting down")
        return
    except Exception as e:
        print(f"Error in acquisition loop: {str(e)}")
        raise

def process_data():
    global heatmap_data, last_update_time
    while True:
        try:
            if data_queue.empty():
                time.sleep(0.01)
                continue
            data = data_queue.get()
            audiolen_samples = len(data[:,0])
            data = data[:int(audiolen_samples/AUDIO_SIZE_REDUCTION_FACTOR)]
            filtered_data = np.zeros_like(data)
            for k in range(CHANNELS):
                filtered_data[:, k] = sp.filtfilt(butter_b, butter_a, data[:, k], padlen=FILTER_PADDING)
            # Use the real heatmap function
            heatmap, _ = data_process_pipe_animated_varyband_sfreqs(filtered_data, fc, bw)
            # Normalize heatmap to 0-1
            heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap))
            heatmap_data = heatmap.tolist()  # Should be 50x5 grid
            last_update_time = time.time()
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            time.sleep(0.1)

app = Flask(__name__)

@app.route('/audio_data', methods=['GET'])
def get_audio_data():
    global ch_data_list
    try:
        audio_data = ch_data_list.T.tolist()
        return jsonify({
            "audio_data": audio_data,
            "sampling_rate": SAMPLING_RATE,
            "channels": CHANNELS,
            "buffer_size": BUFFER_SIZE
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    if heatmap_data is None:
        return jsonify({"error": "No data available"}), 500
    return jsonify({
        "heatmap": heatmap_data,
        "timestamp": last_update_time,
        "dimensions": {
            "length": PIPE_LENGTH_INTERVALS,
            "diameter": PIPE_DIAMETER_INTERVALS
        }
    })

def start_threads():
    threads = [
        threading.Thread(target=acquire_data, daemon=True),
        threading.Thread(target=process_data, daemon=True)
    ]
    for t in threads:
        t.start()

if __name__ == '__main__':
    print("Starting DAQ microservice...")
    start_threads()
    app.run(host='0.0.0.0', port=5002) 