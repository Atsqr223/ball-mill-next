import { notFound } from 'next/navigation';
import { locations } from '@/lib/locations';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData, sensors } from '@/lib/schema';
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
      .select({
        id: acquisitionSessions.id,
        startTime: acquisitionSessions.startTime,
        endTime: acquisitionSessions.endTime,
        status: acquisitionSessions.status,
        metadata: acquisitionSessions.metadata,
        sensorId: acquisitionSessions.sensorId,
      })
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.locationId, locationId))
      .orderBy(acquisitionSessions.createdAt, { order: 'desc' })
      .limit(50);

    const analyses = await Promise.all(
      sessions.map(async (session) => {
        // Get sensor type
        const [sensorInfo] = await db
          .select({
            type: sensors.type,
          })
          .from(sensors)
          .where(eq(sensors.id, session.sensorId));

        // Get sensor data based on type
        const rawData = await db
          .select()
          .from(sensorData)
          .where(eq(sensorData.sessionId, session.id));

        const data = rawData.map(item => {
          const baseData = {
            sampleIndex: item.sampleIndex,
            timestamp: item.timestamp.toISOString(),
          };

          switch (sensorInfo.type) {
            case 'LD':
              return {
                ...baseData,
                value: item.voltage,
                unit: 'V',
              };
            case 'ACCELEROMETER':
              return {
                ...baseData,
                x: item.accelerationX,
                y: item.accelerationY,
                z: item.accelerationZ,
                unit: 'm/s²',
              };
            case 'RADAR':
              return {
                ...baseData,
                value: item.distance,
                unit: 'm',
              };
            default:
              return baseData;
          }
        });

        return {
          session: {
            id: session.id,
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
        <h2 className="text-2xl font-semibold mb-4">Analysis History</h2>
        <AnalysisHistory analyses={recentAnalyses} />
      </div>
    </div>
  );
}
