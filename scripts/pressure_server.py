import asyncio
import websockets
import json
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx import stream_readers
import numpy as np
import time as t

# Server settings
HOST = '0.0.0.0'
PORT = 65506

# DAQ settings
fs = 2  # Sampling rate (Hz)
nSamples = 2  # Number of samples per acquisition
numChannels = 1  # Number of channels to acquire
totalTime = 1  # Time for each acquisition in seconds

# Normalize the pressure data (conversion from voltage to pressure)
def normalize(data):
    return [46.18 * x - 25.7 for x in data]  # Adjust to your sensor's calibration

# Function to acquire DAQ pressure data
def get_daq_pressure():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai1", terminal_config=TerminalConfiguration.RSE)
        task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=AcquisitionType.FINITE, samps_per_chan=nSamples)
        reader = stream_readers.AnalogMultiChannelReader(task.in_stream)

        ch_data_list = []
        t_start = t.time()
        while t.time() - t_start < totalTime:
            buffer = np.zeros((numChannels, nSamples), dtype=np.float64)
            reader.read_many_sample(buffer, nSamples, timeout=nidaqmx.constants.WAIT_INFINITELY)
            ch_data_list.append(buffer[0])  # From channel 0

        normalized_data = normalize(np.concatenate(ch_data_list))
        return normalized_data[-1]  # Return the latest pressure value

# Handle client connections
async def pressure_sender(websocket):
    print("Client connected.")
    try:
        while True:
            pressure_value = get_daq_pressure()
            data = {"pressure": pressure_value}
            await websocket.send(json.dumps(data))
            print(f"Sent pressure: {pressure_value}")
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")

# Start WebSocket server
async def main():
    async with websockets.serve(pressure_sender, HOST, PORT):
        print(f"Pressure WebSocket server started on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
