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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
