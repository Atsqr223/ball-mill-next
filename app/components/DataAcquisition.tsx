'use client'

import { useState } from 'react'
import type { Sensor } from '@/lib/locations'

interface DataAcquisitionProps {
  sensors: Sensor[]
  locationId: number
}

interface SensorDataPoint {
  timestamp: string;
  value?: number;
  x?: number;
  y?: number;
  z?: number;
  unit?: string;
}

export default function DataAcquisition({ sensors, locationId }: DataAcquisitionProps) {
  const [selectedSensor, setSelectedSensor] = useState<number | null>(null)
  const [sensorType, setSensorType] = useState<string>('')
  const [numDataPoints, setNumDataPoints] = useState<number>(100)
  const [isAcquiring, setIsAcquiring] = useState(false)
  const [sensorData, setSensorData] = useState<SensorDataPoint[]>([])
  const [error, setError] = useState<string | null>(null)

  // Update sensor type when sensor selection changes
  const handleSensorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const sensorId = Number(e.target.value);
    setSelectedSensor(sensorId);
    const sensor = sensors.find(s => s.id === sensorId);
    setSensorType(sensor?.type || '');
    setSensorData([]);
    setError(null);
  };

  const handleStartAcquisition = async () => {
    if (!selectedSensor || !sensorType || isAcquiring) return;

    setIsAcquiring(true);
    setSensorData([]);
    setError(null);

    try {
      const response = await fetch('/api/acquisition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          locationId,
          sensorId: selectedSensor,
          numDataPoints,
        }),
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Failed to acquire data');
      }

      if (result.success) {
        setSensorData(result.data);
      } else {
        throw new Error(result.error || 'Failed to acquire data');
      }
    } catch (error) {
      console.error('Error during data acquisition:', error);
      setError(error instanceof Error ? error.message : 'Failed to acquire data');
    } finally {
      setIsAcquiring(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Acquisition</h2>
      
      <div className="space-y-6">
        <div>
          <label htmlFor="sensor" className="block text-sm font-medium text-gray-700 mb-2">
            Select Sensor
          </label>
          <select
            id="sensor"
            value={selectedSensor || ''}
            onChange={handleSensorChange}
            disabled={isAcquiring}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="">Select a sensor</option>
            {sensors.map((sensor) => (
              <option key={sensor.id} value={sensor.id}>
                {sensor.name} ({sensor.type})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="dataPoints" className="block text-sm font-medium text-gray-700 mb-2">
            Number of Data Points
          </label>
          <input
            type="number"
            id="dataPoints"
            min="1"
            max="1000"
            value={numDataPoints}
            onChange={(e) => setNumDataPoints(Number(e.target.value))}
            disabled={isAcquiring}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>

        <div>
          <button
            onClick={handleStartAcquisition}
            disabled={!selectedSensor || isAcquiring}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isAcquiring ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'}`}
          >
            {isAcquiring ? 'Acquiring Data...' : 'Start Acquisition'}
          </button>
        </div>

        {error && (
          <div className="text-red-600 text-sm mt-2">
            {error}
          </div>
        )}

        {isAcquiring && (
          <div className="mt-4">
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                    Progress
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold inline-block text-indigo-600">
                    {Math.round((sensorData.length / numDataPoints) * 100)}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
                <div
                  style={{ width: `${(sensorData.length / numDataPoints) * 100}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"
                />
              </div>
            </div>
          </div>
        )}

        {sensorData.length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Acquired Data</h3>
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-sm text-gray-700 overflow-auto max-h-60">
                {JSON.stringify(sensorData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
