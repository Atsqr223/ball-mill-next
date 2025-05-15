'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import type { Sensor } from '@/lib/locations'

interface DataAcquisitionProps {
  sensors: Sensor[]
  locationId: number
}

export default function DataAcquisition({ sensors, locationId }: DataAcquisitionProps) {
  const router = useRouter()
  const [selectedSensor, setSelectedSensor] = useState<number | null>(null)
  const [numDataPoints, setNumDataPoints] = useState<number>(100)
  const [fileName, setFileName] = useState<string>('')
  const [isAcquiring, setIsAcquiring] = useState(false)

  const handleStartAcquisition = async () => {
    if (!selectedSensor) return

    setIsAcquiring(true)
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const sensor = sensors.find(s => s.id === selectedSensor)
      const defaultFileName = `${timestamp}_${sensor?.name || 'sensor'}`
      
      const response = await fetch('/api/acquisition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          locationId,
          sensorId: selectedSensor,
          numDataPoints,
          fileName: fileName || defaultFileName,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start data acquisition')
      }

      router.refresh()
    } catch (error) {
      console.error('Error starting data acquisition:', error)
    } finally {
      setIsAcquiring(false)
    }
  }

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
            onChange={(e) => setSelectedSensor(Number(e.target.value))}
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
          <label htmlFor="fileName" className="block text-sm font-medium text-gray-700 mb-2">
            File Name (Optional)
          </label>
          <input
            type="text"
            id="fileName"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            disabled={isAcquiring}
            placeholder="Leave empty for auto-generated name"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-sm text-gray-500">
            If not specified, will use timestamp and sensor name
          </p>
        </div>

        <div>
          <button
            onClick={handleStartAcquisition}
            disabled={!selectedSensor || isAcquiring}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
              ${!selectedSensor || isAcquiring
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
          >
            {isAcquiring ? 'Acquiring Data...' : 'Start Acquisition'}
          </button>
        </div>
      </div>
    </div>
  )
} 
