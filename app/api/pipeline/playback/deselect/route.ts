import { NextResponse } from 'next/server';

const PLAYBACK_SERVER_HOST = process.env.PLAYBACK_SERVER_HOST || 'localhost';
const PLAYBACK_SERVER_PORT = process.env.PLAYBACK_SERVER_PORT || '5002';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    // Forward request to playback server
    const response = await fetch(`http://${PLAYBACK_SERVER_HOST}:${PLAYBACK_SERVER_PORT}/deselect_pixel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to deselect pixel' },
        { status: response.status }
      );
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Playback deselect error:', error);
    return NextResponse.json(
      { error: 'Failed to deselect pixel' },
      { status: 500 }
    );
  }
} 