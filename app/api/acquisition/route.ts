import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { sensorData, sensors } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, numDataPoints } = await request.json();

    if (!locationId || !sensorId || !numDataPoints) {
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
      return NextResponse.json(
        { error: 'No data found for this sensor' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: data,
      message: `Successfully retrieved ${data.length} data points`
    });
  } catch (error) {
    console.error('Error in data acquisition:', error);
    return NextResponse.json(
      { error: 'Failed to acquire data' },
      { status: 500 }
    );
  }
}
