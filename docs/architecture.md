# Architecture

## High-Level System Diagram

```
[Python Scripts] <---MQTT/Socket.IO---> [Next.js Backend/API] <---Drizzle ORM---> [PostgreSQL]
                                              |
                                              v
                                    [Next.js Frontend (React)]
                                              |
                                              v
                                    [Plotly.js, YouTubeEmbed]
```

## Major Components
- **Frontend**: Next.js (App Router), React 18, TailwindCSS
- **Backend/API**: Next.js API routes under `/app/api/`
- **Database**: PostgreSQL (Neon) via Drizzle ORM
- **Real-time**: MQTT and Socket.IO for live sensor data
- **Visualization**: Plotly.js for sensor/historical data, YouTubeEmbed for live video
- **Python Scripts**: For sensor/PLC data acquisition, simulation, and integration

## Data Flow
1. **Sensor Data Acquisition**: Python scripts collect data, send via MQTT/Socket.IO to backend.
2. **Data Storage**: Backend stores data in PostgreSQL using Drizzle ORM.
3. **Frontend Visualization**: React components fetch and display real-time/historical data and video.

## Service Boundaries
- **Python scripts** are decoupled from the web app, communicating via MQTT/Socket.IO.
- **API routes** encapsulate business logic and data access.
- **Frontend** is modular, with feature folders and colocated components.

---

See [Directory Structure](./directory-structure.md) for a breakdown of key folders and files.
