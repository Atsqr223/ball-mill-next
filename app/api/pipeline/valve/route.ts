import { NextResponse } from 'next/server';

const PIPELINE_SERVER_HOST = process.env.PIPELINE_SERVER_HOST || 'localhost';
const PIPELINE_SERVER_PORT = process.env.PIPELINE_SERVER_PORT || '5000';

export async function POST(request: Request) {
  try {
    const { valveIndex, state } = await request.json();

    if (valveIndex === undefined || state === undefined) {
      return NextResponse.json(
        { error: 'Valve index and state are required' },
        { status: 400 }
      );
    }

    if (valveIndex < 0 || valveIndex >= 3) {
      return NextResponse.json(
        { error: 'Invalid valve index' },
        { status: 400 }
      );
    }

    // Forward request to Python server
    const response = await fetch(`http://${PIPELINE_SERVER_HOST}:${PIPELINE_SERVER_PORT}/valve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ valveIndex, state }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to control valve' },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Valve control error:', error);
    return NextResponse.json(
      { error: 'Failed to control valve' },
      { status: 500 }
    );
  }
} 