import { NextResponse } from 'next/server'
import { sql } from '@vercel/postgres'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const result = await sql`
      SELECT x, y, z
      FROM ball_mill_positions
      WHERE location_id = ${params.id}
      ORDER BY timestamp DESC
      LIMIT 100
    `

    return NextResponse.json({
      x: result.rows.map(row => row.x),
      y: result.rows.map(row => row.y),
      z: result.rows.map(row => row.z)
    })
  } catch (error) {
    console.error('Error fetching ball mill data:', error)
    return NextResponse.json(
      { error: 'Failed to fetch ball mill data' },
      { status: 500 }
    )
  }
} 