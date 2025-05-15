import { NextResponse } from 'next/server';
import { db } from '@/db';
import { acquisitionSessions, acquisitionData } from '@/db/schema';
import { eq } from 'drizzle-orm';

export async function POST(request: Request) {
  try {
    const { locationId, sensorIds, numDataPoints } = await request.json();

    // Create a new acquisition session
    const [session] = await db
      .insert(acquisitionSessions)
      .values({
        locationId,
        numDataPoints,
        status: 'active',
      })
      .returning();

    // Initialize acquisition data entries for each sensor
    await Promise.all(
      sensorIds.map((sensorId: number) =>
        db.insert(acquisitionData).values({
          sessionId: session.id,
          sensorId,
          dataPoints: [], // Will be populated as data comes in
        })
      )
    );

    return NextResponse.json(session.id);
  } catch (error) {
    console.error('Error starting acquisition:', error);
    return NextResponse.json(
      { error: 'Failed to start acquisition' },
      { status: 500 }
    );
  }
} 