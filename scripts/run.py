import subprocess
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Define the commands to run
commands = [
    "npm run dev",
    "python scripts/pipeline_server.py",
    "python scripts/audio_server.py",
    "python scripts/playback_server.py",
    "python scripts/Siemens_PLC_IO_API.py"
]

# Store subprocesses
processes = []

try:
    for cmd in commands:
        print(f"Starting: {cmd}")
        # Use shell=True for Windows compatibility (especially for npm)
        process = subprocess.Popen(cmd, shell=True, env=os.environ.copy())
        processes.append(process)
    
    print("All processes started. Press Ctrl+C to stop.")
    
    # Keep the main script running while subprocesses are active
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down all processes...")
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()
    print("All processes terminated.")
