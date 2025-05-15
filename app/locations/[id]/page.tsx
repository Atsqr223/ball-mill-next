import { notFound } from 'next/navigation';
import { locations } from '@/lib/locations';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData } from '@/lib/schema';
import { eq } from 'drizzle-orm';
import LiveStream from '@/app/components/LiveStream';
import DataAcquisition from '@/app/components/DataAcquisition';
import AnalysisHistory from '@/app/components/AnalysisHistory';

async function getLocation(id: number) {
  const location = locations.find(loc => loc.id === id);
  if (!location) return null;
  return location;
}

async function getRecentAnalyses(locationId: number) {
  try {
    const sessions = await db
      .select()
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.locationId, locationId))
      .orderBy(acquisitionSessions.createdAt)
      .limit(50);

    const analyses = await Promise.all(
      sessions.map(async (session) => {
        const rawData = await db
          .select({
            value: sensorData.value,
            timestamp: sensorData.timestamp,
          })
          .from(sensorData)
          .where(eq(sensorData.sessionId, session.id));

        const data = rawData.map(item => ({
          value: item.value,
          timestamp: item.timestamp.toISOString(),
        }));

        return {
          session: {
            id: session.id,
            numDataPoints: data.length,
            startTime: session.startTime.toISOString(),
            endTime: session.endTime?.toISOString() || null,
            status: session.status,
          },
          data,
        };
      })
    );

    return analyses;
  } catch (error) {
    console.error('Failed to fetch analyses:', error);
    return [];
  }
}

export default async function LocationPage({
  params,
}: {
  params: { id: string };
}) {
  const locationId = parseInt(params.id);
  const location = await getLocation(locationId);

  if (!location) {
    notFound();
  }

  const recentAnalyses = await getRecentAnalyses(locationId);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">{location.name}</h1>
        <div className="flex items-center">
          <div
            className={`w-3 h-3 rounded-full ${
              location.status === 'active' ? 'bg-green-500' : 'bg-red-500'
            } mr-2`}
          />
          <span className="capitalize">{location.status}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Live Stream</h2>
          <LiveStream streamId={location.youtubeStreamId} />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Data Acquisition</h2>
          <DataAcquisition
            locationId={locationId}
            sensors={location.sensors}
          />
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Recent Analyses</h2>
        <AnalysisHistory analyses={recentAnalyses} />
      </div>
    </div>
  );
} 
