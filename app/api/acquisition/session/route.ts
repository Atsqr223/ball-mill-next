import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { acquisitionSessions } from '@/lib/schema';

export async function POST(request: Request) {
  try {
    const { locationId, sensorId, fileName } = await request.json();

    if (!locationId || !sensorId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const now = new Date();

    // Create a new acquisition session
    const [session] = await db
      .insert(acquisitionSessions)
      .values({
        locationId,
        sensorId,
        status: 'in_progress',
        startTime: now,
        fileName: fileName || `acquisition_${now.toISOString()}`,
        metadata: {},
        sensor_data: {},
      })
      .returning();

    return NextResponse.json({
      success: true,
      sessionId: session.id,
      message: 'Acquisition session created successfully'
    });
  } catch (error) {
    console.error('Error creating acquisition session:', error);
    return NextResponse.json(
      { error: 'Failed to create acquisition session' },
      { status: 500 }
    );
  }
} 
