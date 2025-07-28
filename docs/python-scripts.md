# Python Scripts & Data Acquisition

## Purpose
Python scripts in `scripts/` handle sensor data simulation, PLC integration, and server utilities. They are decoupled from the web app and communicate via MQTT or Socket.IO.

## Key Scripts
- `generate_sensor_data.py`: Simulates sensor data for development/testing.
- `init_locations.py`, `init_sensors.py`: Initialize DB with locations and sensors.
- `mock_pipeline_server.py`, `pipeline_server.py`: Simulate or run pipeline data acquisition.
- `Siemens_PLC_IO_API.py`, `Siemens_PLC_IO_Control.py`: Integrate with Siemens PLCs for real data.
- `audio_server.py`, `pressure_server.py`, `playback_server.py`: Specialized data acquisition servers.
- `upload_sensor_data.py`: Uploads CSV data to the backend.

## Patterns
- Scripts use MQTT/Socket.IO for communication.
- Each script is documented with usage and configuration in docstrings or `readme.txt`.
- Scripts can be extended for new sensor types or protocols.

## Example: Running a Simulation
```bash
python scripts/generate_sensor_data.py --location=1 --sensor=temperature
```

---

See [Developer Workflows](./developer-workflows.md) for how scripts fit into the workflow.
