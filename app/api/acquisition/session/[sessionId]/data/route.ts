import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { sensorData, acquisitionSessions, sensors } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = parseInt(params.sessionId);

    // First verify the session exists
    const [session] = await db
      .select()
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.id, sessionId));

    if (!session) {
      return NextResponse.json(
        { error: 'Acquisition session not found' },
        { status: 404 }
      );
    }

    // Get the sensor type for this session
    const [sensor] = await db
      .select()
      .from(sensors)
      .where(eq(sensors.id, session.sensorId));

    if (!sensor) {
      return NextResponse.json(
        { error: 'Sensor not found' },
        { status: 404 }
      );
    }

    // Get all sensor data points for this session
    const data = await db
      .select()
      .from(sensorData)
      .where(eq(sensorData.acquisitionSessionId, sessionId))
      .orderBy(desc(sensorData.timestamp));

    if (!data || data.length === 0) {
      return NextResponse.json(
        { error: 'No data found for this session' },
        { status: 404 }
      );
    }

    // Format the data based on sensor type
    const formattedData = data.map(point => {
      const baseData = {
        id: point.id,
        timestamp: point.timestamp,
      };

      switch (sensor.type) {
        case 'LD':
          return {
            ...baseData,
            value: point.voltage,
            unit: 'V'
          };
        case 'ACCELEROMETER':
          return {
            ...baseData,
            x: point.accelerationX,
            y: point.accelerationY,
            z: point.accelerationZ,
            unit: 'm/s²'
          };
        case 'RADAR':
          return {
            ...baseData,
            value: point.distance,
            unit: 'm'
          };
        default:
          return baseData;
      }
    });

    return NextResponse.json({
      success: true,
      session: {
        id: session.id,
        status: session.status,
        startTime: session.startTime,
        endTime: session.endTime,
        fileName: session.fileName,
        sensorType: sensor.type,
        numDataPoints: data.length
      },
      data: formattedData
    });
  } catch (error) {
    console.error('Error fetching session data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch session data' },
      { status: 500 }
    );
  }
} 
