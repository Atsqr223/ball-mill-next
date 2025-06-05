import Link from 'next/link';
import { locations, Location as LocationType } from '@/lib/locations';
import LiveStream from '@/app/components/LiveStream'; // Assuming LiveStream might still be used or adapted

// SensorStatus Component (can be shared or adapted if pipeline sensors differ significantly)
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

// LocationCard Component (adapted for pipeline, link updated)
function LocationCard({ location }: { location: LocationType }) {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* You might want a different visual for pipeline locations, e.g., a static image or different component */}
      {/* For now, using LiveStream as a placeholder if applicable, or it can be removed/replaced */}
      {location.youtubeStreamId && (
        <div className="aspect-video">
          <LiveStream streamId={location.youtubeStreamId} />
        </div>
      )}
      {!location.youtubeStreamId && (
         <div className="aspect-video bg-gray-300 flex items-center justify-center">
           <p className="text-gray-500">No Live Stream Available</p>
         </div>
      )}
      
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
            href={`/pipeline-monitoring/locations/${location.id}`} // Updated href
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

export default function PipelineMonitoringPage() {
  const pipelineLocations = locations.filter(loc => loc.type === 'pipeline');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold">Pipeline Conduit Monitoring</h1>
        <Link href="/" className="text-blue-500 hover:text-blue-700">
          &larr; Back to Dashboard
        </Link>
      </div>
      {pipelineLocations.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {pipelineLocations.map((location) => (
            <LocationCard key={location.id} location={location} />
          ))}
        </div>
      ) : (
        <p className="text-gray-600">No Pipeline locations found.</p>
      )}
    </div>
  );
}
