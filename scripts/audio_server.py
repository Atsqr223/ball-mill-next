import sys
import os
import numpy as np
import time
import logging
import threading
import queue
from flask import Flask, jsonify
import nidaqmx
from nidaqmx import stream_readers
from nidaqmx.constants import TerminalConfiguration
import scipy.signal as sp

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup path for module imports
base_dir = os.path.dirname(os.path.abspath(__file__))
pipe_path = os.path.abspath(os.path.join(base_dir, '..', 'pipe'))
sys.path.append(pipe_path)

# Local package imports
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.doa_data_process import data_process_pipe_animated_varyband_sfreqs
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.glob_vars import SAMPLING_RATE, THETA_OFFSET, PIPE_LENGTH_INTERVALS, PIPE_DIAMETER_INTERVALS
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.generate_bpfilt import generate_bpfilt_varyband

# Flask app
app = Flask(__name__)

# Configuration
CHANNELS = 9
CHUNK_SIZE = 200
# Use a larger buffer to ensure we have enough samples for processing
BUFFER_DURATION_SEC = 1 # Buffer duration for DAQ
BUFFER_SIZE = SAMPLING_RATE * BUFFER_DURATION_SEC

# Filter configuration
BAND_DISTANCE = 400
LOWER_FREQ = 1000
UPPER_FREQ = 7000
fc, bw = generate_bpfilt_varyband(BAND_DISTANCE, SAMPLING_RATE, LOWER_FREQ, UPPER_FREQ)

# Global state
task = None
data_queue = queue.Queue(maxsize=500000)
heatmap_data = None
last_update_time = 0
ch_data_list = np.array([np.zeros(BUFFER_SIZE) for i in range(CHANNELS)])

# Process configuration
AUDIO_SIZE_REDUCTION_FACTOR = 4  # Reduce audio size for better time complexity

# Filter configuration
FILTER_ORDER = 5  # Filter order for bandpass filtering
FILTER_PADDING = 100  # Padding for filter operation

# Initialize filter
butter_b, butter_a = sp.butter(FILTER_ORDER, [LOWER_FREQ, UPPER_FREQ], btype='band', fs=SAMPLING_RATE)


def setup_task():
    """Configure and return a NI-DAQmx task and reader"""
    try:
        t = nidaqmx.Task()
        t.ai_channels.add_ai_voltage_chan(f"Dev1/ai1:{CHANNELS}",terminal_config=TerminalConfiguration.RSE)

        # for ch in range(CHANNELS):
        #     t.ai_channels.add_ai_voltage_chan(
        #         f"Dev1/ai{ch}",
        #         terminal_config=TerminalConfiguration.RSE,
        #         min_val=-10.0,
        #         max_val=10.0
        #     )

        t.timing.cfg_samp_clk_timing(
            rate=SAMPLING_RATE,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=BUFFER_SIZE
        )

        in_stream = t.in_stream
        reader = stream_readers.AnalogMultiChannelReader(in_stream)

        return t, reader
    except Exception as e:
        logger.error(f"Failed to set up NI-DAQ task: {e}")
        return None, None


def acquire_data():
    """DAQ acquisition loop (producer)"""
    global task, reader
    try:
        while True:
            if not task or not reader:
                logger.warning("DAQ task or reader not initialized.")
                time.sleep(1)
                continue

            try:
                # Read data from DAQ
                reader.read_many_sample(
                    data=ch_data_list,
                    number_of_samples_per_channel=BUFFER_SIZE
                )

                # Convert to numpy array
                data = np.array(ch_data_list).T

                # Add to processing queue
                data_queue.put(data)

            except Exception as e:
                logger.error(f"Error acquiring data: {str(e)}")
                time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received - shutting down")
        
        return

            # audio_chunk = task.read(number_of_samples_per_channel=CHUNK_SIZE)
            # audio_chunk = np.array(audio_chunk).T  # shape: (samples, channels)

            # try:
            #     data_queue.put_nowait(audio_chunk)
            # except queue.Full:
            #     logger.warning("Data queue full — dropping audio chunk")
    except Exception as e:
        logger.error(f"Error in acquisition loop: {str(e)}")
        raise

def process_data():
    """Processing loop (consumer)"""
    global heatmap_data, last_update_time
    
    while True:
        try:
            if data_queue.empty():
                time.sleep(0.01)
                continue

            # Get data from queue
            data = data_queue.get()
            
            # Reduce audio size for better time complexity
            audiolen_samples = len(data[:,0])
            data = data[:int(audiolen_samples/AUDIO_SIZE_REDUCTION_FACTOR)]
            
            # Apply bandpass filter
            filtered_data = np.zeros_like(data)
            for k in range(CHANNELS):
                filtered_data[:, k] = sp.filtfilt(butter_b, butter_a, data[:, k], padlen=FILTER_PADDING)
            
            # Process data
            heatmap, _ = data_process_pipe_animated_varyband_sfreqs(filtered_data, fc, bw)
            
            # Normalize heatmap
            heatmap = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap))
            
            # Update global state
            heatmap_data = heatmap.tolist()
            last_update_time = time.time()
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            time.sleep(0.1)


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


@app.route('/status', methods=['GET'])
def get_status():
    try:
        running = task.is_task_done() is False if task else False
    except Exception:
        running = False

    return jsonify({
        "is_running": running,
        "last_update": last_update_time,
        "sampling_rate": SAMPLING_RATE,
        "chunk_size": CHUNK_SIZE,
        "queue_size": data_queue.qsize()
    })


def start_threads():
    """Start DAQ and processing threads"""
    global task, reader
    task, reader = setup_task()
    if task is None or reader is None:
        logger.error("DAQ task or reader could not be initialized.")
        sys.exit(1)

    threads = [
        threading.Thread(target=acquire_data, daemon=True),
        threading.Thread(target=process_data, daemon=True)
    ]

    for t in threads:
        t.start()


if __name__ == '__main__':
    try:
        logger.info("Starting audio server...")
        start_threads()
        app.run(host='0.0.0.0', port=5001)

    except KeyboardInterrupt:
        logger.info("Shutting down server...")

    finally:
        try:
            if task:
                task.stop()
                task.close()
                logger.info("DAQ task cleaned up.")
        except Exception as e:
            logger.warning(f"Failed to clean up task: {e}")
