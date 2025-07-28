# Python Integration & Data Acquisition

This section details the core Python scripts that power real-time data acquisition, device control, and advanced signal processing for the Ball Mill Monitoring System. Only actively maintained and production-relevant scripts are documented here.

---

## 1. `audio_server.py`
- **Purpose:** Acquires multi-channel audio from NI-DAQ hardware, processes it (filtering, heatmap generation), and serves real-time results via a Flask API.
- **Key Endpoints:**
  - `/heatmap`: Returns the latest processed heatmap for visualization.
  - `/status`: Reports acquisition status and queue size.
  - `/audio_data`: Streams raw audio data for further processing/playback.
- **Architecture:** Uses producer-consumer threading for DAQ and processing. Integrates with custom signal processing modules and supports real-time web UI.
- **Usage:**
  - Requires NI-DAQ hardware and drivers.
  - Run as a standalone server:
    ```bash
    python scripts/audio_server.py
    ```
  - Consumed by other services (e.g., `playback_server.py`) and the frontend.

## 2. `playback_server.py`
- **Purpose:** Provides interactive audio playback and spatial filtering for selected pixels/regions in the UI, using data from `audio_server.py`.
- **Key Endpoints:**
  - `/select_pixel`: Selects a region for playback, returns filtered audio.
  - `/play`: Starts/stops playback for a selected region.
  - `/deselect_pixel`: Removes a region from playback.
  - `/status`: Reports server and playback status.
- **Architecture:**
  - Fetches audio from `audio_server.py`, applies spatial and low-pass filtering, and streams to the client.
  - Manages multiple concurrent playback streams using `sounddevice`.
- **Usage:**
  - Requires `audio_server.py` to be running.
  - Run as a standalone server:
    ```bash
    python scripts/playback_server.py
    ```

## 3. `pipeline_server.py`
- **Purpose:** Controls physical pipeline valves via GPIO on a Raspberry Pi, exposing a REST API for remote operation.
- **Key Endpoints:**
  - `/connect`: Connects to a remote Pi and initializes valves.
  - `/valve`: Opens/closes a specific valve.
  - `/status`: Reports connection and valve states.
  - `/disconnect`: Safely disconnects and resets all valves.
- **Architecture:**
  - Uses `gpiozero` and `pigpio` for robust remote GPIO control.
  - Designed for safe, idempotent operation with retry logic.
- **Usage:**
  - Run on a server with network access to the target Pi:
    ```bash
    python scripts/pipeline_server.py
    ```

## 4. `pressure_server.py`
- **Purpose:** Streams real-time pressure sensor data over WebSockets for live monitoring.
- **Key Features:**
  - Acquires data from NI-DAQ hardware, normalizes using calibration, and streams to clients.
  - Designed for low-frequency, high-reliability pressure monitoring.
- **Usage:**
  - Run as a standalone async server:
    ```bash
    python scripts/pressure_server.py
    ```
  - Consumed by frontend or other services via WebSocket.

## 5. `Siemens_PLC_IO_API.py` and `Siemens_PLC_IO_Control.py`
- **Purpose:** Integrate with Siemens PLCs for direct I/O control and monitoring.
- **Features:**
  - `Siemens_PLC_IO_API.py`: Flask API for remote PLC bit manipulation.
  - `Siemens_PLC_IO_Control.py`: Script for direct, programmatic PLC control.
- **Usage:**
  - Requires `snap7` library and network access to the PLC.
  - Run as needed for automation or integration.

---

Scripts not listed here are deprecated or scheduled for removal. For advanced integration or extension, see the rest of the documentation suite.
