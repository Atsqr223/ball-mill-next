import { notFound } from 'next/navigation';
import Link from 'next/link';
import { locations, Location as LocationType } from '@/lib/locations';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData, sensors } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';
import LiveStream from '@/app/components/LiveStream';
import DataAcquisition from '@/app/components/DataAcquisition';
import AnalysisHistory from '@/app/components/AnalysisHistory';

async function getLocation(locationId: number) {
  // Ensure we only get ball-mill locations if needed, though finding by ID should be specific enough.
  const location = locations.find(loc => loc.id === locationId && loc.type === 'ball-mill');
  if (!location) return null;
  return location;
}

async function getRecentAnalyses(locationId: number) {
  try {
    const sessions = await db
      .select({
        id: acquisitionSessions.id,
        startTime: acquisitionSessions.startTime,
        endTime: acquisitionSessions.endTime,
        status: acquisitionSessions.status,
        metadata: acquisitionSessions.metadata as Record<string, any>,
        sensorId: acquisitionSessions.sensorId,
        fileName: acquisitionSessions.fileName,
      })
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.locationId, locationId))
      .orderBy(desc(acquisitionSessions.startTime));

    const analyses = await Promise.all(
      sessions.map(async (session) => {
        const [sensorInfo] = await db
          .select({
            type: sensors.type,
          })
          .from(sensors)
          .where(eq(sensors.id, session.sensorId));

        const rawData = await db
          .select()
          .from(sensorData)
          .where(eq(sensorData.acquisitionSessionId, session.id));

        const data = rawData.map(item => ({
          id: item.id,
          timestamp: item.timestamp.toISOString(),
          sensor_time: item.sensorTime || 0,
          x: item.accelerationX || undefined,
          y: item.accelerationY || undefined,
          z: item.accelerationZ || undefined,
          distance: item.distance || undefined,
          radar: item.radar || undefined,
          acceleration_x: item.accelerationX || undefined,
          acceleration_y: item.accelerationY || undefined,
          acceleration_z: item.accelerationZ || undefined,
          unit: sensorInfo.type === 'LD' ? 'm' : 
                sensorInfo.type === 'ACCELEROMETER' ? 'm/s²' :
                sensorInfo.type === 'RADAR' ? 'm' : undefined
        }));

        return {
          session: {
            id: session.id,
            fileName: session.fileName,
            numDataPoints: data.length,
            startTime: session.startTime.toISOString(),
            endTime: session.endTime?.toISOString() || null,
            status: session.status,
            sensorType: sensorInfo.type,
            metadata: session.metadata,
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

export default async function BallMillLocationPage({
  params,
}: {
  params: { locationId: string };
}) {
  const locationId = parseInt(params.locationId);
  const location = await getLocation(locationId);

  if (!location) {
    notFound();
  }

  const recentAnalyses = await getRecentAnalyses(locationId);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-4xl font-bold">{location.name}</h1>
          <Link href="/ball-mill" className="text-blue-500 hover:text-blue-700">
            &larr; Back to Ball Mill Locations
          </Link>
        </div>
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
        <h2 className="text-2xl font-semibold mb-4">Analysis History</h2>
        <AnalysisHistory analyses={recentAnalyses} locationId={locationId} />
      </div>
    </div>
  );
}
