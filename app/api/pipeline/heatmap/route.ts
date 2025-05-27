import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Forward request to audio server
    const response = await fetch('http://localhost:5001/heatmap');

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
