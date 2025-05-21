import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { piIp } = await request.json();

    if (!piIp) {
      return NextResponse.json(
        { error: 'Raspberry Pi IP address is required' },
        { status: 400 }
      );
    }

    // Forward request to Python server
    const response = await fetch('http://localhost:5000/connect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ piIp }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to connect to Raspberry Pi' },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Connection error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to Raspberry Pi' },
      { status: 500 }
    );
  }
} 