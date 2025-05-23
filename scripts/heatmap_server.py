from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import time
import threading
from live_demo_dependencies.DOA_supporting_functions import *
from live_demo_dependencies.generate_bpfilt import *
from live_demo_dependencies.glob_vars import *
from live_demo_dependencies.doa_data_process import *

app = Flask(__name__)
CORS(app)

# Configuration
SAMPLING_RATE = 48000  # Hz
BAND_DISTANCE = 400  # Hz
FREQUENCY_FILTERING_ON = True
AUDIO_SIZE_REDUCTION_FACTOR = 4

# Generate bandpass filter
fc, bw = generate_bpfilt_varyband(
    BAND_DISTANCE=BAND_DISTANCE,
    R_b=SAMPLING_RATE,
    lower_freq=1000,
    upper_freq=7000,
    tapered=True
)

def get_audio_data():
    try:
        pkl_file = open('pickles/audio_file.pkl', 'rb')
        audio_data = pickle.load(pkl_file)
        pkl_file.close()

        # Shorten audio for better time complexity
        audiolen_samples = len(audio_data[:, 0])
        audio_data = audio_data[:int(audiolen_samples/AUDIO_SIZE_REDUCTION_FACTOR)]
        return audio_data
    except Exception as e:
        print(f"Error reading audio data: {e}")
        return None

def compute_heatmap():
    audio_data = get_audio_data()
    if audio_data is None:
        return None

    # Find pmusic composite map and single frequency maps
    p_music, _ = data_process_pipe_animated_varyband_sfreqs(
        audio_data,
        fc,
        bw,
        magType='linadd',
        theta_offset=180
    )

    # Normalize pmusic
    minval = np.min(p_music)
    maxval = np.max(p_music)
    p_music = (p_music - minval) / (maxval - minval)

    return p_music.T.tolist()

# Global variable to store the latest heatmap data
latest_heatmap = None
heatmap_lock = threading.Lock()

def update_heatmap():
    global latest_heatmap
    while True:
        try:
            new_heatmap = compute_heatmap()
            if new_heatmap is not None:
                with heatmap_lock:
                    latest_heatmap = new_heatmap
        except Exception as e:
            print(f"Error computing heatmap: {e}")
        time.sleep(0.1)  # Update every 100ms

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
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5001, debug=True) 
