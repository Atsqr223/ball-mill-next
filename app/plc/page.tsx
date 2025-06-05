import Link from 'next/link';
import { locations, Location as LocationType } from '@/lib/locations';

// Minimal SensorStatus for PLC (can be expanded later)
function SensorStatus({ type, status }: { type: string; status: 'active' | 'inactive' }) {
  return (
    <div className="flex items-center space-x-2">
      <div 
        className={`w-2 h-2 rounded-full ${
          status === 'active' ? 'bg-green-500' : 'bg-red-500'
        }`} 
      />
      <span className="text-sm text-gray-600">{type}</span>
    </div>
  );
}

// Minimal LocationCard for PLC (can be expanded later)
function LocationCard({ location }: { location: LocationType }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="p-4">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-semibold mb-1">{location.name}</h2>
            <div className="flex items-center">
              <div 
                className={`w-3 h-3 rounded-full ${
                  location.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                } mr-2`} 
              />
              <span className="capitalize text-sm text-gray-600">{location.status}</span>
            </div>
          </div>
          <Link 
            href={`/plc/locations/${location.id}`} // Updated href
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            View Details
          </Link>
        </div>
        <div className="border-t pt-3">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Sensors</h3>
          {location.sensors && location.sensors.length > 0 ? (
            <div className="grid grid-cols-2 gap-2">
              {location.sensors.map((sensor) => (
                <SensorStatus key={sensor.id} type={sensor.type} status={sensor.status} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No sensor information available.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PLCPage() {
  const plcLocations = locations.filter(loc => loc.type === 'plc');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold">PLC Systems</h1>
        <Link href="/" className="text-blue-500 hover:text-blue-700">
          &larr; Back to Dashboard
        </Link>
      </div>
      <p className="mb-6 text-lg text-gray-700">Manage and monitor Programmable Logic Controllers. (Full functionality coming soon)</p>
      {plcLocations.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {plcLocations.map((location) => (
            <LocationCard key={location.id} location={location} />
          ))}
        </div>
      ) : (
        <p className="text-gray-600">No PLC locations found.</p>
      )}
    </div>
  );
}
