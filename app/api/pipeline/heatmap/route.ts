import { NextResponse } from 'next/server';

const AUDIO_SERVER_HOST = process.env.AUDIO_SERVER_HOST || 'localhost';
const AUDIO_SERVER_PORT = process.env.AUDIO_SERVER_PORT || '5001';

export async function GET() {
  try {
    // Forward request to audio server
    const response = await fetch(`http://${AUDIO_SERVER_HOST}:${AUDIO_SERVER_PORT}/heatmap`);

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to fetch heatmap data' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Heatmap fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch heatmap data' },
      { status: 500 }
    );
  }
}
