import { notFound } from 'next/navigation';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData, sensors } from '@/lib/schema';
import { eq } from 'drizzle-orm';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function formatTimeAgo(date: Date) {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  const intervals = [
    { label: 'second', seconds: 60 },
    { label: 'minute', seconds: 3600 },
    { label: 'hour', seconds: 86400 },
    { label: 'day', seconds: 2592000 },
    { label: 'month', seconds: 31536000 },
    { label: 'year', seconds: Infinity },
  ];

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count >= 1) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
    }
  }

  return 'just now';
}

function formatTimestamp(timestamp: Date) {
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
}

interface PageProps {
  params: {
    locationId: string;
    sessionId: string;
  };
}

async function getSession(sessionId: number) {
  const [session] = await db
    .select()
    .from(acquisitionSessions)
    .where(eq(acquisitionSessions.id, sessionId));

  if (!session) return null;

  const [sensorInfo] = await db
    .select()
    .from(sensors)
    .where(eq(sensors.id, session.sensorId));

  const rawData = await db
    .select()
    .from(sensorData)
    .where(eq(sensorData.acquisitionSessionId, session.id))
    .orderBy(sensorData.sensorTime);

  console.log('Session:', session);
  console.log('Sensor Info:', sensorInfo);
  console.log('Raw Data Sample:', rawData.slice(0, 3));

  return {
    session,
    sensorInfo,
    data: rawData
  };
}

export default async function AcquisitionSessionPage({ params }: PageProps) {
  const sessionId = parseInt(params.sessionId);
  const result = await getSession(sessionId);

  if (!result) {
    notFound();
  }

  const { session, sensorInfo, data } = result;

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="mb-8">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl">
                {session.fileName || `Session #${session.id}`}
              </CardTitle>
              <p className="text-sm text-gray-500 mt-1">
                Started {formatTimeAgo(new Date(session.startTime))}
              </p>
            </div>
            <Badge variant={session.status === 'completed' ? 'success' : 'warning'}>
              {session.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Sensor Type</p>
              <p className="font-medium">{sensorInfo.type}</p>
            </div>
            <div>
              <p className="text-gray-500">Data Points</p>
              <p className="font-medium">{data.length}</p>
            </div>
            <div>
              <p className="text-gray-500">Start Time</p>
              <p className="font-medium">{formatTimestamp(session.startTime)}</p>
            </div>
            {session.endTime && (
              <div>
                <p className="text-gray-500">End Time</p>
                <p className="font-medium">{formatTimestamp(session.endTime)}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Raw Data Points</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">ID</th>
                  <th className="text-left py-2">Sensor Time</th>
                  <th className="text-left py-2">Radar</th>
                  <th className="text-left py-2">Acceleration X</th>
                  <th className="text-left py-2">Acceleration Y</th>
                  <th className="text-left py-2">Acceleration Z</th>
                  <th className="text-left py-2">Distance</th>
                </tr>
              </thead>
              <tbody>
                {data.map((point) => (
                  <tr key={point.id} className="border-b">
                    <td className="py-2">{point.id}</td>
                    <td className="py-2">{point.sensorTime?.toString()}</td>
                    <td className="py-2">{point.radar?.toFixed(6)}</td>
                    <td className="py-2">{point.accelerationX?.toFixed(6)}</td>
                    <td className="py-2">{point.accelerationY?.toFixed(6)}</td>
                    <td className="py-2">{point.accelerationZ?.toFixed(6)}</td>
                    <td className="py-2">{point.distance?.toFixed(6)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
