import Link from 'next/link';
import { locations } from '@/lib/locations';
import LiveStream from '@/app/components/LiveStream';

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

function LocationCard({ location }: { location: typeof locations[0] }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="aspect-video">
        <LiveStream streamId={location.youtubeStreamId} />
      </div>
      
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
            href={`/locations/${location.id}`}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            View Details
          </Link>
        </div>

        <div className="border-t pt-3">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Sensors</h3>
          <div className="grid grid-cols-2 gap-2">
            {location.sensors.map((sensor) => (
              <SensorStatus key={sensor.id} type={sensor.type} status={sensor.status} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Ball Mill Monitoring System</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
        {locations.map((location) => (
          <LocationCard key={location.id} location={location} />
        ))}
      </div>
    </div>
  );
}
