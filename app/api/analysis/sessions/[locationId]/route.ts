import { NextResponse } from 'next/server';
import { db } from '@/db';
import { acquisitionSessions } from '@/db/schema';
import { eq, desc } from 'drizzle-orm';

export async function GET(
  request: Request,
  { params }: { params: { locationId: string } }
) {
  try {
    const locationId = parseInt(params.locationId);

    // Get the most recent 50 completed sessions for this location
    const sessions = await db
      .select()
      .from(acquisitionSessions)
      .where(eq(acquisitionSessions.locationId, locationId))
      .orderBy(desc(acquisitionSessions.startTime))
      .limit(50);

    return NextResponse.json(sessions);
  } catch (error) {
    console.error('Error fetching sessions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch sessions' },
      { status: 500 }
    );
  }
} 