import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { acquisitionSessions, sensorData } from '@/lib/schema';

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, numDataPoints, fileName } = await request.json();

    if (!locationId || !sensorId || !numDataPoints) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
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
      })
      .returning();

    // Simulate data acquisition (replace with actual data acquisition logic)
    const mockData = Array.from({ length: numDataPoints }, (_, i) => ({
      sessionId: session.id,
      sensorId,
      value: Math.random() * 100, // Replace with actual sensor reading
      timestamp: new Date(Date.now() + i * 1000), // Simulate 1-second intervals
    }));

    // Insert sensor data
    await db.insert(sensorData).values(mockData);

    // Update session status
    await db
      .update(acquisitionSessions)
      .set({
        status: 'completed',
        endTime: new Date(),
      })
      .where({ id: session.id });

    return NextResponse.json({ success: true, sessionId: session.id });
  } catch (error) {
    console.error('Error in data acquisition:', error);
    return NextResponse.json(
      { error: 'Failed to acquire data' },
      { status: 500 }
    );
  }
} 
