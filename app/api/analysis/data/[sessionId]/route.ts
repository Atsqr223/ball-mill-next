import { NextResponse } from 'next/server';
import { db } from '@/db';
import { acquisitionData } from '@/db/schema';
import { eq } from 'drizzle-orm';

export async function GET(
  request: Request,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = parseInt(params.sessionId);

    // Get all acquisition data entries for this session
    const dataEntries = await db
      .select()
      .from(acquisitionData)
      .where(eq(acquisitionData.sessionId, sessionId));

    if (dataEntries.length === 0) {
      return NextResponse.json(
        { error: 'No data found for this session' },
        { status: 404 }
      );
    }

    // For now, we'll just return the first sensor's data
    // In a real implementation, you might want to handle multiple sensors differently
    const firstEntry = dataEntries[0];

    return NextResponse.json({
      dataPoints: firstEntry.dataPoints,
      analysisResults: firstEntry.analysisResults || {
        mean: 0,
        std: 0,
        fft: [],
      },
    });
  } catch (error) {
    console.error('Error fetching analysis data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analysis data' },
      { status: 500 }
    );
  }
} 