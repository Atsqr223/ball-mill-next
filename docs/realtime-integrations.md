# Real-Time Data & Integrations

## Real-Time Data Flow
- **Sensor data** is acquired by Python scripts and sent to the backend via MQTT or Socket.IO.
- **Backend** receives, validates, and stores data in PostgreSQL.
- **Frontend** subscribes to real-time updates via Socket.IO/MQTT and updates UI components live.

## Integration Points
- **MQTT Broker**: Used for sensor data ingestion from Python scripts.
- **Socket.IO**: Used for pushing real-time updates to the frontend.
- **YouTube API**: Used for embedding live video streams per location.
- **Python Scripts**: For data acquisition, simulation, and PLC integration (see `scripts/`).

## Example: Real-Time Sensor Update
- Python script publishes to MQTT topic (e.g., `sensors/location1/temperature`).
- Backend API route subscribes and stores data.
- Frontend component subscribes to updates and re-renders Plotly.js chart.

---

See [Python Scripts & Data Acquisition](./python-scripts.md) for script details.
