import { NextResponse } from 'next/server';

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
    const response = await fetch('http://localhost:5002/select_pixel', {
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
    console.error('Pixel selection error:', error);
    return NextResponse.json(
      { error: 'Failed to select pixel' },
      { status: 500 }
    );
  }
} 