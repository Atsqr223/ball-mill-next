import sys
import os
import numpy as np
import time
import logging
import threading
from flask import Flask, jsonify
import nidaqmx
from nidaqmx import Task
from nidaqmx.constants import TerminalConfiguration, AcquisitionType, AcquisitionType
import ctypes

# Add parent and pipe directories to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
pipe_path = os.path.abspath(os.path.join(base_dir, '..', 'pipe'))
sys.path.append(pipe_path)

# Now import using package-style syntax
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.doa_data_process import data_process_pipe_animated_varyband_sfreqs
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.glob_vars import SAMPLING_RATE, THETA_OFFSET, PIPE_LENGTH_INTERVALS, PIPE_DIAMETER_INTERVALS
from N_MIC_LIVEDEMO_PLAYBACK.live_demo_dependencies.generate_bpfilt import generate_bpfilt_varyband

# Generate BPF parameters
BAND_DISTANCE = 400  # Hz
lower_freq = 1000
upper_freq = 7000
fc, bw = generate_bpfilt_varyband(BAND_DISTANCE, SAMPLING_RATE, lower_freq, upper_freq)

import threading
import time
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

# Store heatmap data and timestamp
heatmap_data = None
last_update_time = 0

# Configure NI-DAQ
CHANNELS = 9
SAMPLING_RATE = 48000
CHUNK_SIZE = 256  # Reduced chunk size for better real-time performance
BUFFER_SIZE = CHUNK_SIZE * 4  # Smaller buffer

# Initialize NI-DAQ task
task = None

# Function to initialize NI-DAQ task
# Configure NI-DAQ with finite acquisition mode
CHANNELS = 9
SAMPLING_RATE = 48000
CHUNK_SIZE = 256  # Reduced chunk size for better real-time performance
BUFFER_SIZE = CHUNK_SIZE * 4  # Smaller buffer

# Global variables for audio processing
heatmap_data = None
last_update_time = 0

# Initialize NI-DAQ task
task = None

# Function to acquire a single chunk of data using NI-DAQmx C API
def acquire_data():
    """Acquire a single chunk of data from NI-DAQ using C API"""
    try:
        # Import NI-DAQmx C API
        nidaqmx = ctypes.windll.nicaiu
        
        # Constants
        DAQmx_Val_Cfg_Default = 10142
        DAQmx_Val_Volts = 10348
        DAQmx_Val_RSE = 10083
        DAQmx_Val_FiniteSamps = 10178
        DAQmx_Val_GroupByChannel = 0
        
        # Create task
        taskHandle = ctypes.c_ulonglong(0)
        nidaqmx.DAQmxCreateTask(b"", ctypes.byref(taskHandle))
        
        # Create channels
        channels = b"Dev1/ai0:8"  # All 9 channels
        min_val = ctypes.c_double(-10.0)
        max_val = ctypes.c_double(10.0)
        units = ctypes.c_int(DAQmx_Val_Volts)
        
        nidaqmx.DAQmxCreateAIVoltageChan(
            taskHandle,
            channels,
            b"",
            ctypes.c_int(DAQmx_Val_RSE),
            min_val,
            max_val,
            units,
            b""
        )
        
        # Configure timing
        sampleRate = ctypes.c_double(SAMPLING_RATE)
        sampsPerChan = ctypes.c_ulonglong(CHUNK_SIZE)
        
        nidaqmx.DAQmxCfgSampClkTiming(
            taskHandle,
            b"",
            sampleRate,
            ctypes.c_int(DAQmx_Val_Cfg_Default),
            ctypes.c_int(DAQmx_Val_FiniteSamps),
            sampsPerChan
        )
        
        # Start task
        nidaqmx.DAQmxStartTask(taskHandle)
        
        # Read data
        read = ctypes.c_int32(0)
        data = np.zeros((CHANNELS, CHUNK_SIZE), dtype=np.float64)
        data_ptr = data.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        nidaqmx.DAQmxReadAnalogF64(
            taskHandle,
            CHUNK_SIZE,
            ctypes.c_double(1.0),  # timeout
            ctypes.c_int(DAQmx_Val_GroupByChannel),
            data_ptr,
            CHANNELS * CHUNK_SIZE,
            ctypes.byref(read),
            None
        )
        
        # Stop and clear task
        nidaqmx.DAQmxStopTask(taskHandle)
        nidaqmx.DAQmxClearTask(taskHandle)
        
        return data.T

    except Exception as e:
        logger.error(f"Error acquiring data: {str(e)}")
        return None

def process_audio():
    """Continuously process audio data and update heatmap"""
    global heatmap_data, last_update_time
    
    while True:
        try:
            # Acquire a chunk of data
            audio_data = acquire_data()
            if audio_data is None:
                time.sleep(0.1)
                continue

            # Process audio data to get heatmap
            heatmap, _ = data_process_pipe_animated_varyband_sfreqs(
                audio_data,
                fc,
                bw,
                magType='linadd',
                theta_offset=THETA_OFFSET
            )
            
            # Update shared data
            heatmap_data = heatmap.tolist()
            last_update_time = time.time()
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            time.sleep(1)  # Wait before retrying

if __name__ == '__main__':
    try:
        # Start audio processing thread
        audio_thread = threading.Thread(target=process_audio, daemon=True)
        audio_thread.start()
        
        logger.info("Starting audio server...")
        app.run(host='0.0.0.0', port=5001)

    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        # Clean up any existing tasks
        try:
            if 'task' in globals():
                if task is not None:
                    task.stop()
                    task.close()
        except:
            pass
        
        try:
            if 'audio_thread' in globals():
                if audio_thread.is_alive():
                    audio_thread.join(timeout=1.0)
        except:
            pass



def process_audio():
    """Continuously process audio data and update heatmap"""
    global heatmap_data, last_update_time
    
    while True:
        try:
            # Read audio data
            audio_data = task.read(number_of_samples_per_channel=CHUNK_SIZE)
            audio_data = np.array(audio_data).T  # Transpose to match expected format
            
            # Process audio data to get heatmap
            heatmap, _ = data_process_pipe_animated_varyband_sfreqs(
                audio_data,
                fc,  # Frequency centers (from glob_vars)
                bw,  # Bandwidth (from glob_vars)
                magType='linadd',
                theta_offset=THETA_OFFSET
            )
            
            # Update shared data
            heatmap_data = heatmap.tolist()
            last_update_time = time.time()
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            time.sleep(1)  # Wait before retrying

@app.route('/heatmap', methods=['GET'])
def get_heatmap():
    """Get latest heatmap data"""
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
    """Get server status"""
    return jsonify({
        "is_running": task.is_task_done,
        "last_update": last_update_time,
        "sampling_rate": SAMPLING_RATE,
        "chunk_size": CHUNK_SIZE
    })

if __name__ == '__main__':
    # Start audio processing thread
    audio_thread = threading.Thread(target=process_audio, daemon=True)
    audio_thread.start()
    
    logger.info("Starting audio server...")
    app.run(host='0.0.0.0', port=5001)
