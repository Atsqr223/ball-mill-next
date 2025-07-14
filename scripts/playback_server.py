import sys
import os
import numpy as np
import time
import logging
import threading
import queue
from flask import Flask, request, jsonify
import requests
import sounddevice as sd
from scipy import signal
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.audio_utils import get_angles_from_pixels_pipe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)

# Constants
CHANNELS = 8  # Number of audio channels
CHUNK_SIZE = 1024  # Number of samples per chunk
BUFFER_DURATION = 1.0  # Duration of audio buffer in seconds
SAMPLING_RATE = 44100  # Sampling rate in Hz
LPF_CUTOFF = 1000  # Low-pass filter cutoff frequency in Hz
LPF_ORDER = 4  # Filter order (higher = sharper cutoff)

# Global variables
audio_buffer = queue.Queue(maxsize=int(SAMPLING_RATE * BUFFER_DURATION / CHUNK_SIZE))
is_acquiring = False
audio_server_ready = False
selected_pixels = {}  # Dictionary to store selected pixels and their audio streams
is_playing = False
audio_streams = {}  # Dictionary to store audio streams for each pixel

def get_audio_data():
    """Get audio data from the audio server."""
    try:
        AUDIO_SERVER_HOST = os.environ.get('AUDIO_SERVER_HOST', 'localhost')
        AUDIO_SERVER_PORT = os.environ.get('AUDIO_SERVER_PORT', '5001')
        response = requests.get(f'http://{AUDIO_SERVER_HOST}:{AUDIO_SERVER_PORT}/audio_data')
        if response.status_code == 200:
            data = response.json()
            return np.array(data['audio_data']), data['sampling_rate']
        else:
            logger.error(f"Failed to get audio data: {response.status_code}")
            return None, None
    except Exception as e:
        logger.error(f"Error getting audio data: {str(e)}")
        return None, None

def acquire_data():
    """Continuously acquire audio data from the audio server."""
    global is_acquiring, audio_server_ready
    is_acquiring = True
    retry_count = 0
    max_retries = 3
    retry_delay = 1.0  # Initial delay in seconds

    while is_acquiring:
        try:
            audio_data, sampling_rate = get_audio_data()
            if audio_data is not None:
                audio_server_ready = True
                retry_count = 0  # Reset retry count on success
                retry_delay = 1.0  # Reset retry delay
                
                # Ensure correct shape
                if len(audio_data.shape) == 1:
                    audio_data = audio_data.reshape(-1, 1)
                
                # Log audio data shape and stats
                logger.info(f"Received audio data: shape={audio_data.shape}, min={np.min(audio_data):.3f}, max={np.max(audio_data):.3f}")
                
                # Add to buffer
                if not audio_buffer.full():
                    audio_buffer.put(audio_data)
                else:
                    audio_buffer.get()  # Remove oldest data
                    audio_buffer.put(audio_data)
                
                # Update audio for all selected pixels
                for pixel_id, stream in audio_streams.items():
                    if stream and stream.active:
                        audio_data = get_audio_for_pixel(*pixel_id)
                        if audio_data is not None:
                            # Use filtered audio for playback
                            playback_data = np.array(audio_data['filtered'], dtype=np.float32)
                            stream.write(playback_data)
            else:
                audio_server_ready = False
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error("Max retries reached, stopping acquisition")
                    is_acquiring = False
                    break
                logger.warning(f"Failed to get audio data, retry {retry_count}/{max_retries}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        except Exception as e:
            logger.error(f"Error in data acquisition: {str(e)}")
            audio_server_ready = False
            retry_count += 1
            if retry_count >= max_retries:
                logger.error("Max retries reached, stopping acquisition")
                is_acquiring = False
                break
            logger.warning(f"Error in data acquisition, retry {retry_count}/{max_retries}")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

def get_audio_for_pixel(x, y):
    """Get audio data for a specific pixel using spatial filtering."""
    global audio_buffer
    
    if not audio_server_ready:
        logger.error("Audio server is not ready")
        return None
    
    if audio_buffer.empty():
        logger.error("Audio buffer is empty")
        return None
    
    try:
        # Get the latest audio data
        audio_data = audio_buffer.queue[-1]
        
        # Convert pixel coordinates to angles
        angles = get_angles_from_pixels_pipe(x, y)
        if angles is None:
            logger.error(f"Invalid pixel coordinates: ({x}, {y})")
            return None
            
        theta, phi = angles
        logger.info(f"Pixel ({x}, {y}) converted to angles: theta={theta:.2f}, phi={phi:.2f}")
        
        # Apply spatial filtering
        # Ensure audio_data is 2D with shape (samples, channels)
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Create a weight matrix for each channel based on angles
        weights = np.zeros((audio_data.shape[1],))
        for i in range(audio_data.shape[1]):
            # Calculate weight based on channel position
            channel_angle = 2 * np.pi * i / audio_data.shape[1]
            weights[i] = np.cos(theta - channel_angle) * np.sin(phi)
        
        # Normalize weights
        weights = weights / np.sum(np.abs(weights))
        
        # Apply weights to each channel and sum
        filtered_audio = np.sum(audio_data * weights, axis=1)
        
        # Normalize the output
        if np.max(np.abs(filtered_audio)) > 0:
            filtered_audio = filtered_audio / np.max(np.abs(filtered_audio))
        
        # Apply low-pass filter
        nyquist = SAMPLING_RATE / 2
        normalized_cutoff = LPF_CUTOFF / nyquist
        b, a = signal.butter(LPF_ORDER, normalized_cutoff, btype='low')
        low_pass_audio = signal.filtfilt(b, a, filtered_audio)
        
        # Normalize low-pass filtered signal
        if np.max(np.abs(low_pass_audio)) > 0:
            low_pass_audio = low_pass_audio / np.max(np.abs(low_pass_audio))
        
        return {
            'raw': filtered_audio.tolist(),
            'filtered': low_pass_audio.tolist()
        }
    except Exception as e:
        logger.error(f"Error getting audio for pixel ({x}, {y}): {str(e)}")
        return None

@app.route('/select_pixel', methods=['POST'])
def select_pixel():
    """Handle pixel selection for playback."""
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        
        if x is None or y is None:
            return jsonify({'error': 'Missing x or y coordinates'}), 400
            
        pixel_id = (x, y)
        audio_data = get_audio_for_pixel(x, y)
        
        if audio_data is None:
            return jsonify({'error': 'Failed to get audio data for selected pixel'}), 500
            
        # Store the pixel selection
        selected_pixels[pixel_id] = {
            'x': x,
            'y': y,
            'is_playing': False
        }
            
        return jsonify({
            'status': 'success',
            'audio_data': audio_data,  # This contains both raw and filtered data
            'sampling_rate': SAMPLING_RATE
        })
    except Exception as e:
        logger.error(f"Error selecting pixel: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/play', methods=['POST'])
def play():
    """Handle audio playback control."""
    global audio_streams
    
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        
        if x is None or y is None:
            return jsonify({'error': 'Missing pixel coordinates'}), 400
            
        pixel_id = (x, y)
        if pixel_id not in selected_pixels:
            return jsonify({'error': 'Pixel not selected'}), 400
            
        if selected_pixels[pixel_id]['is_playing']:
            # Stop playback
            if pixel_id in audio_streams and audio_streams[pixel_id]:
                audio_streams[pixel_id].stop()
                audio_streams[pixel_id].close()
                audio_streams[pixel_id] = None
            selected_pixels[pixel_id]['is_playing'] = False
            return jsonify({'status': 'stopped'})
        else:
            # Start playback
            audio_stream = sd.OutputStream(
                samplerate=SAMPLING_RATE,
                channels=1,
                dtype=np.float32,
                callback=None  # We'll write data manually
            )
            audio_stream.start()
            audio_streams[pixel_id] = audio_stream
            selected_pixels[pixel_id]['is_playing'] = True
            
            # Get initial audio data
            audio_data = get_audio_for_pixel(x, y)
            if audio_data is not None:
                # Use filtered audio for playback
                playback_data = np.array(audio_data['filtered'], dtype=np.float32)
                audio_stream.write(playback_data)
            
            return jsonify({'status': 'playing'})
    except Exception as e:
        logger.error(f"Error controlling playback: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/deselect_pixel', methods=['POST'])
def deselect_pixel():
    """Handle pixel deselection."""
    global audio_streams, selected_pixels
    
    try:
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        
        if x is None or y is None:
            return jsonify({'error': 'Missing pixel coordinates'}), 400
            
        pixel_id = (x, y)
        
        # Stop and remove audio stream if it exists
        if pixel_id in audio_streams:
            if audio_streams[pixel_id]:
                audio_streams[pixel_id].stop()
                audio_streams[pixel_id].close()
            del audio_streams[pixel_id]
        
        # Remove pixel from selection
        if pixel_id in selected_pixels:
            del selected_pixels[pixel_id]
            logger.info(f"Deselected pixel ({x}, {y})")
            return jsonify({'status': 'success'})
        else:
            logger.warning(f"Attempted to deselect non-selected pixel ({x}, {y})")
            return jsonify({'error': 'Pixel not selected'}), 400
            
    except Exception as e:
        logger.error(f"Error deselecting pixel: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the playback server."""
    return jsonify({
        'is_acquiring': is_acquiring,
        'audio_server_ready': audio_server_ready,
        'selected_pixels': selected_pixels,
        'audio_streams': {str(k): v is not None for k, v in audio_streams.items()}
    })

def start_threads():
    """Start the data acquisition thread and Flask app."""
    global is_acquiring
    
    # Start data acquisition thread
    acquire_thread = threading.Thread(target=acquire_data)
    acquire_thread.daemon = True
    acquire_thread.start()
    
    # Start Flask app
    host = os.environ.get('PLAYBACK_SERVER_HOST', '0.0.0.0')
    port = int(os.environ.get('PLAYBACK_SERVER_PORT', 5002))
    app.run(host=host, port=port)

if __name__ == '__main__':
    try:
        start_threads()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        is_acquiring = False
        for stream in audio_streams.values():
            if stream:
                stream.stop()
                stream.close()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        is_acquiring = False
        for stream in audio_streams.values():
            if stream:
                stream.stop()
                stream.close() 