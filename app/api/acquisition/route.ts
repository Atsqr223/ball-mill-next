import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData, sensors } from '@/lib/schema';
import { eq } from 'drizzle-orm';

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, data, fileName } = await request.json();

    if (!locationId || !sensorId || !data || !Array.isArray(data)) {
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

    // Create acquisition session
    const [session] = await db
      .insert(acquisitionSessions)
      .values({
        locationId,
        sensorId,
        status: 'in_progress',
        startTime: new Date(),
        fileName: fileName || null,
        metadata: { sensorType: sensor.type },
      })
      .returning();

    // Process and insert sensor data based on sensor type
    const sensorReadings = data.map((reading: any, index: number) => {
      const baseReading = {
        sessionId: session.id,
        sensorId,
        sampleIndex: index,
        timestamp: new Date(Date.now() + index * 1000), // Simulate 1-second intervals
        metadata: {}, // Additional metadata if needed
      };

      switch (sensor.type) {
        case 'LD':
          return {
            ...baseReading,
            voltage: parseFloat(reading),
          };
        case 'ACCELEROMETER':
          const [x, y, z] = reading.split(',').map(Number);
          return {
            ...baseReading,
            accelerationX: x,
            accelerationY: y,
            accelerationZ: z,
          };
        case 'RADAR':
          return {
            ...baseReading,
            distance: parseFloat(reading),
          };
        default:
          throw new Error(`Unsupported sensor type: ${sensor.type}`);
      }
    });

    // Insert sensor data
    await db.insert(sensorData).values(sensorReadings);

    // Update session status
    await db
      .update(acquisitionSessions)
      .set({
        status: 'completed',
        endTime: new Date(),
      })
      .where(eq(acquisitionSessions.id, session.id));

    return NextResponse.json({ success: true, sessionId: session.id });
  } catch (error) {
    console.error('Error in data acquisition:', error);
    return NextResponse.json(
      { error: 'Failed to acquire data' },
      { status: 500 }
    );
  }
}
