# Extending the System

## Adding a New Sensor Type
1. Update `lib/schema.ts` to define the new sensor and its data structure.
2. Update relevant API routes in `app/api/` to handle the new sensor.
3. Extend or create Python scripts in `scripts/` for data acquisition.
4. Add or update UI components in `components/` for visualization.

## Adding a New Location
1. Insert a new row in the `locations` table (see `init_locations.py`).
2. Add the YouTube stream ID for live video.
3. Update Python scripts to simulate/acquire data for the new location.
4. Add UI elements for the new location in the frontend.

## Extending Data Visualization
1. Create new React components in `components/`.
2. Update data fetching logic in the relevant `app/` feature folder.
3. Use Plotly.js for new types of plots or dashboards.

## Integrating New PLCs or Protocols
- Add new Python scripts or extend existing ones in `scripts/`.
- Update backend API routes to handle new data formats.
- Document new integration points in the `docs/` folder.

---

See [References](./references.md) for key files and further reading.
