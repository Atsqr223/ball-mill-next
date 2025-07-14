import { NextRequest, NextResponse } from 'next/server';

const PLC_SERVER_HOST = process.env.PLC_SERVER_HOST || 'localhost';
const PLC_SERVER_PORT = process.env.PLC_SERVER_PORT || '5010';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const res = await fetch(`http://${PLC_SERVER_HOST}:${PLC_SERVER_PORT}/plc-io`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Proxy error' }, { status: 500 });
  }
} 