# Directory Structure

This project uses a modular, feature-oriented structure. Key directories and their roles:

- `app/` – Next.js App Router pages, API routes, and feature folders:
  - `ball-mill/`, `pipeline/`, `plc/`, `something/`: Feature folders for each monitored system.
  - `api/`: API endpoints for acquisition, analysis, ball-mill data, locations, and pipeline.
- `components/` – Reusable React components:
  - UI elements in `components/ui/` (button, card, heatmap, etc.)
  - Data display: `DataAcquisition.tsx`, `DataAnalysis.tsx`, `LiveStream.tsx`, `LocationCard.tsx`, etc.
- `lib/` – Core logic and configuration:
  - `schema.ts`: Database schema (locations, sensors, sessions, data, positions)
  - `db.ts`: Drizzle ORM config and DB access
  - `utils.ts`: Utility functions
- `data/` – Example sensor data CSVs for development/testing
- `scripts/` – Python scripts for data simulation, PLC integration, and server utilities:
  - `generate_sensor_data.py`, `init_locations.py`, `mock_pipeline_server.py`, `Siemens_PLC_IO_API.py`, etc.
- `public/` – Static assets (images, SVGs, demo images)

**Example:**
- To add a new feature (e.g., a new pipeline monitor), create a folder in `app/`, add UI in `components/`, and update API routes in `app/api/`.

---

See [Database Schema](./database-schema.md) for details on the DB structure.
