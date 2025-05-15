import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { locations } from '@/lib/schema';
import { handleDatabaseError } from '@/lib/db';
import { eq } from 'drizzle-orm';

export async function GET() {
  try {
    const allLocations = await db.select().from(locations);
    return NextResponse.json(allLocations);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch locations' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, youtubeStreamId } = body;

    if (!name) {
      return NextResponse.json(
        { error: 'Name is required' },
        { status: 400 }
      );
    }

    const [newLocation] = await db
      .insert(locations)
      .values({
        name,
        youtubeStreamId,
        status: 'active',
      })
      .returning();

    return NextResponse.json(newLocation, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create location' },
      { status: 500 }
    );
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const { id, name, youtubeStreamId, status } = body;

    if (!id) {
      return NextResponse.json(
        { error: 'Location ID is required' },
        { status: 400 }
      );
    }

    const [updatedLocation] = await db
      .update(locations)
      .set({
        name,
        youtubeStreamId,
        status,
        updatedAt: new Date(),
      })
      .where(eq(locations.id, id))
      .returning();

    if (!updatedLocation) {
      return NextResponse.json(
        { error: 'Location not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(updatedLocation);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update location' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Location ID is required' },
        { status: 400 }
      );
    }

    const [deletedLocation] = await db
      .delete(locations)
      .where(eq(locations.id, parseInt(id)))
      .returning();

    if (!deletedLocation) {
      return NextResponse.json(
        { error: 'Location not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(deletedLocation);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete location' },
      { status: 500 }
    );
  }
} 
