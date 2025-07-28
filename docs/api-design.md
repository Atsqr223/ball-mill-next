# API Design

The backend uses Next.js App Router API routes under `/app/api/` for all data operations.

## Key Endpoints
- **/api/ball-mill-data/[id]** (GET): Get real-time ball mill position data for a location.
- **/api/acquisition/start** (POST): Start a new data acquisition session.
- **/api/acquisition/[id]** (GET): Get acquisition session status and data.
- **/api/locations** (GET/POST): List or add monitored locations.
- **/api/analysis/**: Endpoints for historical data analysis.
- **/api/pipeline/**: Endpoints for pipeline monitoring and data.

## Patterns
- API routes are colocated with feature folders in `app/`.
- Use Drizzle ORM for all DB access (see `lib/db.ts`).
- Real-time updates are pushed via MQTT/Socket.IO, not HTTP polling.
- Data validation and transformation are handled in route handlers.

## Example: Starting a Data Acquisition Session
```ts
// ...existing code...
export async function POST(req: Request) {
  // Parse request, validate, start session, return session ID
}
```

---

See [Frontend & UI](./frontend-ui.md) for how APIs are consumed.
