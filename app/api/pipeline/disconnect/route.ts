import { NextResponse } from 'next/server';

const PIPELINE_SERVER_HOST = process.env.PIPELINE_SERVER_HOST || 'localhost';
const PIPELINE_SERVER_PORT = process.env.PIPELINE_SERVER_PORT || '5000';

export async function POST(request: Request) {
  try {
    // Forward request to Python server
    const response = await fetch(`http://${PIPELINE_SERVER_HOST}:${PIPELINE_SERVER_PORT}/disconnect`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.error || 'Failed to disconnect' },
        { status: response.status }
      );
    }
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Disconnect error:', error);
    return NextResponse.json(
      { error: 'Failed to disconnect' },
      { status: 500 }
    );
  }
}