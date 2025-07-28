# Frontend & UI

## Frameworks & Libraries
- **Next.js 14** (App Router)
- **React 18**
- **TailwindCSS** for styling
- **Plotly.js** for data visualization

## Component Patterns
- UI components are colocated in `components/` and `app/[feature]/components/`.
- Design system elements (button, card, alert, etc.) are in `components/ui/`.
- Data display and control components: `DataAcquisition.tsx`, `DataAnalysis.tsx`, `LiveStream.tsx`, `LocationCard.tsx`, etc.
- Live video is embedded per location using `YouTubeEmbed.tsx`.

## Data Fetching
- Uses React hooks and Next.js data fetching patterns (e.g., `fetch`, `useEffect`).
- Real-time updates via Socket.IO/MQTT subscriptions.
- Data is visualized using Plotly.js components.

## Example: Embedding a Live Stream
```tsx
<YouTubeEmbed streamId={location.youtubeStreamId} />
```

---

See [Real-Time Data & Integrations](./realtime-integrations.md) for live data handling.
