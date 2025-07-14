import { NextResponse } from 'next/server';

const PIPELINE_SERVER_HOST = process.env.PIPELINE_SERVER_HOST || 'localhost';
const PIPELINE_SERVER_PORT = process.env.PIPELINE_SERVER_PORT || '5000';

export async function GET() {
  try {
    // Forward request to Python server
    const response = await fetch(`http://${PIPELINE_SERVER_HOST}:${PIPELINE_SERVER_PORT}/status`);

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to get status' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Status check error:', error);
    return NextResponse.json(
      { error: 'Failed to check status' },
      { status: 500 }
    );
  }
} 