# Database Schema

The system uses PostgreSQL (Neon) with Drizzle ORM. The schema is defined in `lib/schema.ts` and accessed via `lib/db.ts`.

## Main Tables
- **locations**: Ball mill/pipeline locations, YouTube stream IDs, and metadata.
- **sensors**: Sensor configurations per location (type, units, calibration, etc.).
- **acquisition_sessions**: Records of data acquisition sessions (start/end, status, location).
- **sensor_data**: Time-stamped sensor readings (session, sensor, value, timestamp).
- **ball_mill_positions**: Real-time ball mill position data (location, timestamp, position vector).

## Example Schema (see `lib/schema.ts`)
```ts
// ...existing code...
export const locations = pgTable('locations', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 128 }),
  youtubeStreamId: varchar('youtube_stream_id', { length: 64 }),
  // ...other fields...
});
// ...other tables...
```

## Extending the Schema
- To add a new sensor type, update `sensors` and `sensor_data` tables.
- For new features, add tables and update Drizzle models in `lib/schema.ts`.

---

See [API Design](./api-design.md) for how the schema is used in endpoints.
