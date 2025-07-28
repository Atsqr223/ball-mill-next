# Pipeline Monitoring & Control – Manual

## Overview
The pipeline section provides real-time monitoring, visualization, and remote control of industrial pipeline valves and sensors. It integrates with physical devices (Raspberry Pi, PLCs, DAQ hardware) and exposes a modern web UI for operators.

---

## 1. User Interface (UI)

### Main Pipeline Page (`app/pipeline/page.tsx`)
- **Connection:** Enter the Raspberry Pi IP and connect/disconnect to the remote GPIO controller.
- **Valve Control:** Toggle three physical valves (Left, Center, Right) with immediate UI feedback and robust error handling.
- **Compressor (PLC) Control:** Toggle a compressor output via PLC integration.
- **Pressure Display:** Shows real-time pressure readings (via WebSocket from `pressure_server.py`).
- **Live Video:** Embedded YouTube stream for visual monitoring.
- **Acoustics Heatmap:** Real-time heatmap overlay (from `audio_server.py`) visualizes acoustic localization data, aligned with a pipeline image.

### Pipeline Monitoring Dashboard (`app/pipeline-monitoring/page.tsx`)
- **Location Cards:** Lists all pipeline locations, their live status, and available sensors.
- **Navigation:** Click a location to view detailed controls and live data.

### Location Details (`app/pipeline-monitoring/locations/[locationId]/page.tsx`)
- **Contextual Controls:** Renders the full pipeline control UI for the selected location, including real-time pressure and video.

---

## 2. Backend/API Integration

### API Routes (`app/api/pipeline/`)
- **/connect:** Forwards connection requests to the Python `pipeline_server.py` (`POST /connect`).
- **/status:** Fetches current connection and valve states from the Python server (`GET /status`).
- **/valve:** Toggles a specific valve (`POST /valve`).
- **/disconnect:** Safely disconnects and resets all valves (`POST /disconnect`).
- **/heatmap:** Fetches the latest heatmap from the audio server (`GET /heatmap`).
- **/plc-io:** Proxies PLC output control to the Siemens PLC API server (`POST /plc-io`).

All API routes act as proxies, ensuring the Next.js backend remains stateless and device-agnostic.

---

## 3. Python Services

### `pipeline_server.py`
- **Purpose:** Controls physical valves via GPIO on a Raspberry Pi.
- **Endpoints:** `/connect`, `/valve`, `/status`, `/disconnect`.
- **Features:** Robust connection management, retry logic, and safe cleanup.

### `pressure_server.py`
- **Purpose:** Streams real-time pressure sensor data over WebSockets.
- **Integration:** Consumed by the frontend for live pressure display.

### `audio_server.py`
- **Purpose:** Acquires and processes multi-channel audio for acoustic localization.
- **Integration:** Provides heatmap data for the UI.

### `Siemens_PLC_IO_API.py`
- **Purpose:** Exposes a REST API for PLC output control (e.g., compressor).

---

## 4. Data Flow
1. **User connects to a pipeline location** via the web UI.
2. **Next.js API routes** forward commands to the appropriate Python service.
3. **Python services** interact with hardware (GPIO, DAQ, PLC) and return results.
4. **UI updates** in real time, reflecting device state, pressure, and acoustic data.

---

## 5. Key Functionalities
- **Valve Control:** Safe, real-time toggling of physical pipeline valves.
- **Compressor/PLC Control:** Remote toggling of compressor output via Siemens PLC.
- **Pressure Monitoring:** Live pressure readings via DAQ and WebSocket.
- **Acoustic Localization:** Real-time heatmap overlays for leak detection or event localization.
- **Live Video:** Embedded YouTube streams for visual context.
- **Robust Error Handling:** All device interactions are validated, with user feedback on failures.

---

## 6. Extending the Pipeline System
- **Add a new location:** Update the `locations` data and provide a YouTube stream ID.
- **Add new sensors:** Extend the backend and Python services to support new sensor types.
- **Integrate new hardware:** Add or update Python services and proxy API routes as needed.

---

## 7. Troubleshooting
- **Connection Issues:** Ensure the Raspberry Pi and PLC are reachable on the network.
- **Valve/PLC Errors:** Check Python service logs for hardware or communication errors.
- **No Heatmap/Pressure:** Ensure `audio_server.py` and `pressure_server.py` are running and accessible.
- **UI Not Updating:** Check browser console and API route responses for errors.

---

## 8. Codebase Structure (Summary)
- `app/pipeline/` – Main pipeline control UI.
- `app/pipeline-monitoring/` – Dashboard and per-location views.
- `app/api/pipeline/` – API routes proxying to Python services.
- `scripts/` – Python services for device control and data acquisition.
- `components/ui/` – UI building blocks (cards, switches, heatmap, etc.).
- `public/pipe_leakage/` – Pipeline images for visualization overlays.

---

This manual should enable new developers and operators to understand, operate, and extend the pipeline monitoring and control system with confidence. For more, see the rest of the documentation suite.
