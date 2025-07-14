import { NextResponse } from 'next/server';

const PLAYBACK_SERVER_HOST = process.env.PLAYBACK_SERVER_HOST || 'localhost';
const PLAYBACK_SERVER_PORT = process.env.PLAYBACK_SERVER_PORT || '5002';

export async function POST(request: Request) {
  try {
    const { x, y } = await request.json();

    if (x === undefined || y === undefined) {
      return NextResponse.json(
        { error: 'Pixel coordinates are required' },
        { status: 400 }
      );
    }

    // Forward request to playback server
    const response = await fetch(`http://${PLAYBACK_SERVER_HOST}:${PLAYBACK_SERVER_PORT}/select_pixel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ x, y }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to select pixel' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Playback Pixel select error:', error);
    return NextResponse.json(
      { error: 'Failed to select pixel' },
      { status: 500 }
    );
  }
} 