# Ball Mill Monitoring System

A modern web application for monitoring and analyzing ball mill operations across multiple locations.

## Features

- Real-time monitoring of multiple ball mill locations
- Live YouTube video streams for each location
- Real-time sensor data visualization
- Data acquisition from multiple sensors
- Historical data analysis
- Interactive 3D ball mill visualization

## Tech Stack

- **Frontend**: Next.js 14, React 18, TailwindCSS
- **Database**: PostgreSQL (Neon)
- **ORM**: Drizzle ORM
- **Real-time**: MQTT, Socket.IO
- **Visualization**: Plotly.js

## Prerequisites

- Node.js 18 or later
- PostgreSQL database (Neon)
- MQTT broker
- YouTube API credentials (for live streaming)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ball-mill-next
   ```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Fill in the environment variables with your values.

4. Push the database schema:
```bash
   npm run db:push
```

5. Start the development server:
```bash
npm run dev
```

## Project Structure

- `/app` - Next.js app router pages and components
- `/lib` - Utility functions, database schema, and configurations
- `/components` - Reusable React components
- `/public` - Static assets

## Database Schema

- `locations` - Ball mill locations and their YouTube stream IDs
- `sensors` - Sensor configurations for each location
- `acquisition_sessions` - Data acquisition session records
- `sensor_data` - Collected sensor data with timestamps
- `ball_mill_positions` - Real-time ball mill position data

## API Routes

- `GET /api/ball-mill-data/[id]` - Get real-time ball mill position data
- `POST /api/acquisition/start` - Start a new data acquisition session
- `GET /api/acquisition/[id]` - Get acquisition session status and data

## Control Server and Client Usage

### 1. Install Dependencies

From the project root, install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Start the Control Server

Run the control server (it will listen on port 65507):

```bash
python scripts/control_server.py
```

The server will automatically connect to the pressure WebSocket and expose a REST API for control.

### 3. Use the Control Client

You can use the control client to send commands to the server:

```bash
# Toggle valve 0 ON
python scripts/control_client.py valve 0 on

# Toggle valve 1 OFF
python scripts/control_client.py valve 1 off

# Turn compressor ON
python scripts/control_client.py compressor on

# Turn compressor OFF
python scripts/control_client.py compressor off

# Set pressure threshold to 2.5 (auto-off compressor when reached)
python scripts/control_client.py threshold 2.5

# Get current status (pressure, threshold, compressor state)
python scripts/control_client.py status
```

### Notes
- The control server uses the website's API endpoints for all actions.
- The pressure threshold is configurable at runtime via the client.
- The server will auto-switch off the compressor when the threshold is reached.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
