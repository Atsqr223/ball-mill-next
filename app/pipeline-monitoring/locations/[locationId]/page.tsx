'use client'; // Keep 'use client' if PipelineControl needs it, or manage state accordingly

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { locations, Location as LocationType } from '@/lib/locations';
import PipelineControl from '../../../pipeline/page';
import { useEffect, useState } from 'react';

export default function PipelineLocationPage() {
  const params = useParams();
  const locationIdString = params.locationId as string;
  const [location, setLocation] = useState<LocationType | null>(null);
  const [pressure, setPressure] = useState<number | null>(null);

  useEffect(() => {
    if (locationIdString) {
      const id = parseInt(locationIdString);
      const foundLocation = locations.find(loc => loc.id === id && loc.type === 'pipeline');
      if (foundLocation) {
        setLocation(foundLocation);
      } else {
        // Handle not found outside of useEffect or ensure notFound can be called here
        // For simplicity, we'll rely on a check before rendering.
        setLocation(null); 
      }
    }
  }, [locationIdString]);

  // WebSocket connection for real-time pressure
  useEffect(() => {
    // Update the URL below to your Azure VM's public IP and port, e.g. ws://YOUR_AZURE_IP:65506
    const wsUrl = process.env.NEXT_PUBLIC_PRESSURE_WS_URL || 'ws://localhost:65506';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (typeof data.pressure === 'number') {
          setPressure(data.pressure);
        }
      } catch (e) {
        // Ignore malformed data
      }
    };
    ws.onerror = () => {
      // Optionally handle error
    };
    return () => {
      ws.close();
    };
  }, []);

  if (!locationIdString) {
    // This case should ideally be handled by Next.js routing if the param is missing
    return <p>Loading location...</p>; 
  }

  if (!location) {
    // Call notFound() if the component is intended to be a server component initially
    // or handle as an error/loading state for client components.
    // For a client component that might initially not have the param, then finds it invalid:
    // notFound(); // This might need to be called from a Server Component parent or specific Next.js API
    return <p>Pipeline location not found.</p>; // Fallback for client-side not found
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-4xl font-bold">{location.name}</h1>
          <Link href="/pipeline-monitoring" className="text-blue-500 hover:text-blue-700">
            &larr; Back to Pipeline Locations
          </Link>
        </div>
        {/* Real-time pressure value display */}
        </div>
      {/* All original pipeline controls and logic */}
      <PipelineControl youtubeStreamId={location.youtubeStreamId} pressure={pressure}   />
    </div>
  );
}
