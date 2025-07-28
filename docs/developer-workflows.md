# Developer Workflows

## Environment Setup
1. Clone the repository.
2. Install dependencies: `npm install`
3. Copy `.env.example` to `.env` and fill in DB, MQTT, and YouTube API credentials.
4. Push DB schema: `npm run db:push`
5. Start dev server: `npm run dev`

## Running Python Scripts
- From `scripts/`, run simulation or integration scripts as needed (see script docstrings/readme).
- Example: `python scripts/generate_sensor_data.py`

## Database Management
- Schema is managed in `lib/schema.ts`.
- Use Drizzle ORM for migrations and queries.

## Debugging & Testing
- Use browser dev tools and Next.js error overlays for frontend debugging.
- Use logging in Python scripts and backend API routes for tracing data flow.
- Test data acquisition and visualization with example CSVs in `data/`.

## Extending the System
- Add new sensors/locations by updating DB schema, API routes, and Python scripts.
- Add new UI features by creating components in `components/` and updating feature folders in `app/`.

---

See [Extending the System](./extending.md) for more advanced extension patterns.
