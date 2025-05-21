import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { sensorData, sensors, acquisitionSessions } from '@/lib/schema';
import { eq, desc, and, inArray } from 'drizzle-orm';

// Normalize sensor type to match schema
function normalizeSensorType(type: string): string {
  const normalized = type.toUpperCase();
  if (normalized === 'AUDIO') return 'ACCELEROMETER';
  if (normalized === 'LASER_DISTANCE') return 'LD';
  return normalized;
}

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, numDataPoints, sessionId } = await request.json();

    if (!locationId || !sensorId || !numDataPoints || !sessionId) {
      return NextResponse.json(
        { error: 'Missing required fields or invalid data format' },
        { status: 400 }
      );
    }

    // Get sensor type
    const [sensor] = await db
      .select()
      .from(sensors)
      .where(eq(sensors.id, sensorId));

    if (!sensor) {
      return NextResponse.json(
        { error: 'Sensor not found' },
        { status: 404 }
      );
    }

    // Get the most recent sensor data points
    const data = await db
      .select()
      .from(sensorData)
      .where(eq(sensorData.sensorId, sensorId))
      .orderBy(desc(sensorData.timestamp))
      .limit(numDataPoints);

    if (!data || data.length === 0) {
      // Update session status to failed
      await db
        .update(acquisitionSessions)
        .set({ 
          status: 'failed',
          endTime: new Date(),
          metadata: { error: 'No data found for this sensor' }
        })
        .where(eq(acquisitionSessions.id, sessionId));

      return NextResponse.json(
        { error: 'No data found for this sensor' },
        { status: 404 }
      );
    }

    // Update all the sensor data points to link them to this session
    await db
      .update(sensorData)
      .set({ 
        acquisitionSessionId: sessionId
      })
      .where(inArray(sensorData.id, data.map(point => point.id)));

    // Update session status to completed with normalized sensor type
    await db
      .update(acquisitionSessions)
      .set({ 
        status: 'completed',
        endTime: new Date(),
        metadata: { 
          numDataPoints: data.length,
          sensorType: normalizeSensorType(sensor.type)
        }
      })
      .where(eq(acquisitionSessions.id, sessionId));

    return NextResponse.json({
      success: true,
      data: data,
      message: `Successfully linked ${data.length} data points to session`
    });
  } catch (error) {
    console.error('Error in data acquisition:', error);
    
    // Update session status to failed if sessionId exists
    try {
      const requestData = await request.json();
      if (requestData.sessionId) {
        await db
          .update(acquisitionSessions)
          .set({ 
            status: 'failed',
            endTime: new Date(),
            metadata: { error: 'Failed to acquire data' }
          })
          .where(eq(acquisitionSessions.id, requestData.sessionId));
      }
    } catch (updateError) {
      console.error('Error updating session status:', updateError);
    }

    return NextResponse.json(
      { error: 'Failed to acquire data' },
      { status: 500 }
    );
  }
}
