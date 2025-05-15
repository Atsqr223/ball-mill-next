import { NextResponse } from 'next/server';
import { db } from '@/db';
import { acquisitionSessions, acquisitionData } from '@/db/schema';
import { eq } from 'drizzle-orm';

interface DataPoint {
  timestamp: string;
  value: number;
}

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = parseInt(params.sessionId);

    // Get the session
    const session = await db
      .select()
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.id, sessionId))
      .limit(1)
      .then(rows => rows[0]);

    if (!session) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    // Get all acquisition data entries for this session
    const dataEntries = await db
      .select()
      .from(acquisitionData)
      .where(eq(acquisitionData.sessionId, sessionId));

    // Calculate progress based on the number of data points collected
    const totalDataPoints = dataEntries.reduce((sum: number, entry) => {
      const points = entry.dataPoints as DataPoint[];
      return sum + points.length;
    }, 0);

    const targetDataPoints = session.numDataPoints * dataEntries.length;
    const progress = Math.min(100, Math.round((totalDataPoints / targetDataPoints) * 100));

    return NextResponse.json({
      progress,
      status: session.status,
    });
  } catch (error) {
    console.error('Error checking progress:', error);
    return NextResponse.json(
      { error: 'Failed to check progress' },
      { status: 500 }
    );
  }
} 