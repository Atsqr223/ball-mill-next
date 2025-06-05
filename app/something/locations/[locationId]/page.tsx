'use client';

import Link from 'next/link';
import { useParams, notFound } from 'next/navigation';
import { locations, Location as LocationType } from '@/lib/locations';
import { useEffect, useState } from 'react';

export default function SomethingLocationPage() {
  const params = useParams();
  const locationIdString = params.locationId as string;
  const [location, setLocation] = useState<LocationType | null>(null);

  useEffect(() => {
    if (locationIdString) {
      const id = parseInt(locationIdString);
      const foundLocation = locations.find(loc => loc.id === id && loc.type === 'something');
      if (foundLocation) {
        setLocation(foundLocation);
      } else {
        setLocation(null);
      }
    }
  }, [locationIdString]);

  if (!locationIdString) {
    return <p>Loading location...</p>;
  }

  if (!location) {
    return <p>'Something' location not found.</p>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-4xl font-bold">{location.name} - 'Something' Details</h1>
          <Link href="/something" className="text-blue-500 hover:text-blue-700">
            &larr; Back to 'Something' Locations
          </Link>
        </div>
        <div className="flex items-center">
          <div
            className={`w-3 h-3 rounded-full ${
              location.status === 'active' ? 'bg-green-500' : 'bg-red-500'
            } mr-2`}
          />
          <span className="capitalize">{location.status}</span>
        </div>
      </div>

      <div className="bg-gray-100 p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Feature Coming Soon</h2>
        <p className="text-gray-700">
          Detailed information for this 'Something' location ({location.name}) will be available soon.
        </p>
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800">Sensors at this location:</h3>
          {location.sensors && location.sensors.length > 0 ? (
            <ul className="list-disc list-inside mt-2 text-gray-600">
              {location.sensors.map(sensor => (
                <li key={sensor.id}>{sensor.name} ({sensor.type}) - <span className={sensor.status === 'active' ? 'text-green-600' : 'text-red-600'}>{sensor.status}</span></li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">No sensor information available for this location.</p>
          )}
        </div>
      </div>
    </div>
  );
}
