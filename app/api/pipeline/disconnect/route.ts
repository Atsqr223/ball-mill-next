import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // Forward request to Python server
    const response = await fetch('http://localhost:5000/disconnect', {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to disconnect from Raspberry Pi' },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Disconnect error:', error);
    return NextResponse.json(
      { error: 'Failed to disconnect from Raspberry Pi' },
      { status: 500 }
    );
  }
}