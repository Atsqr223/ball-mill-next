'use client'; // Keep 'use client' if PipelineControl needs it, or manage state accordingly

import Link from 'next/link';
import { useParams, notFound } from 'next/navigation'; // Import useParams
import { locations, Location as LocationType } from '@/lib/locations';
import PipelineControl from '../../../pipeline/page'; // Corrected path to the original PipelineControl
import { useEffect, useState } from 'react';

export default function PipelineLocationPage() {
  const params = useParams();
  const locationIdString = params.locationId as string;
  const [location, setLocation] = useState<LocationType | null>(null);

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
        {/* You can add other location-specific details here if needed */}
      </div>
      {/* Render the existing PipelineControl component */}
      <PipelineControl />
    </div>
  );
}
