import { NextResponse } from 'next/server';
import { db } from '@/db';
import { acquisitionSessions, sensorData, sensors } from '@/db/schema';
import { eq, desc } from 'drizzle-orm';

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, numDataPoints } = await request.json();

    if (!locationId || !sensorId || !numDataPoints) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required fields',
        },
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
        {
          success: false,
          error: 'Sensor not found',
        },
        { status: 404 }
      );
    }

    // Get the most recent sensor data points
    const data = await db
      .select({
        id: sensorData.id,
        value: sensorData.value,
        timestamp: sensorData.timestamp,
      })
      .from(sensorData)
      .where(eq(sensorData.sensorId, sensorId))
      .orderBy(desc(sensorData.timestamp))
      .limit(numDataPoints);

    if (!data || data.length === 0) {
      return NextResponse.json(
        {
          success: false,
          error: 'No data found for the specified sensor',
        },
        { status: 404 }
      );
    }

    // Create a new acquisition session
    const [session] = await db
      .insert(acquisitionSessions)
      .values({
        locationId,
        numDataPoints,
        status: 'completed',
        startTime: new Date(),
        endTime: new Date(),
      })
      .returning();

    // Format the response data
    const formattedData = data.map(point => ({
      timestamp: point.timestamp,
      value: point.value,
    }));

    return NextResponse.json({ 
      success: true,
      sessionId: session.id,
      sensorType: sensor.type,
      data: formattedData,
      message: `Successfully acquired ${data.length} data points`
    });
  } catch (error) {
    console.error('Error during data acquisition:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to acquire data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 