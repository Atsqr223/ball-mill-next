import { notFound } from 'next/navigation';
import { locations } from '@/lib/locations';
import { db } from '@/lib/db';
import { sensors, acquisitionSessions, sensorData } from '@/lib/schema';
import { eq } from 'drizzle-orm';
import LiveStream from '@/app/components/LiveStream';
import DataAcquisition from '@/app/components/DataAcquisition';
import AnalysisHistory from '@/app/components/AnalysisHistory';

async function getLocation(id: number) {
  const location = locations.find(loc => loc.id === id);
  if (!location) return null;
  return location;
}

async function getLocationSensors(locationId: number) {
  try {
    return await db
      .select()
      .from(sensors)
      .where(eq(sensors.locationId, locationId));
  } catch (error) {
    console.error('Failed to fetch sensors:', error);
    return [];
  }
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
        const data = await db
          .select()
          .from(sensorData)
          .where(eq(sensorData.sessionId, session.id));
        return { session, data };
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

  const sensors = await getLocationSensors(locationId);
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
            sensors={sensors}
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
