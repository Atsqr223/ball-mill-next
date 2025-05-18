import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { acquisitionSessions, sensors } from '@/lib/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const locationId = searchParams.get('locationId');

    if (!locationId) {
      return NextResponse.json(
        { error: 'Location ID is required' },
        { status: 400 }
      );
    }

    // Get all acquisition sessions for this location
    const sessions = await db
      .select({
        id: acquisitionSessions.id,
        fileName: acquisitionSessions.fileName,
        status: acquisitionSessions.status,
        startTime: acquisitionSessions.startTime,
        endTime: acquisitionSessions.endTime,
        sensorType: sensors.type,
        metadata: acquisitionSessions.metadata,
      })
      .from(acquisitionSessions)
      .leftJoin(sensors, eq(acquisitionSessions.sensorId, sensors.id))
      .where(eq(acquisitionSessions.locationId, parseInt(locationId)))
      .orderBy(desc(acquisitionSessions.startTime));

    // Format the sessions with safe metadata handling
    const formattedSessions = sessions.map(session => ({
      id: session.id,
      fileName: session.fileName,
      status: session.status,
      startTime: session.startTime,
      endTime: session.endTime,
      sensorType: session.sensorType,
      numDataPoints: session.metadata?.numDataPoints || 0,
    }));

    return NextResponse.json({
      success: true,
      sessions: formattedSessions
    });
  } catch (error) {
    console.error('Error fetching acquisition sessions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch acquisition sessions' },
      { status: 500 }
    );
  }
} 
