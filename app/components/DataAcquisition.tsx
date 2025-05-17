'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Sensor } from '@/lib/locations'

interface DataAcquisitionProps {
  sensors: Sensor[]
  locationId: number
}

interface SensorData {
  LD: { voltage: number }[]
  ACCELEROMETER: { x: number; y: number; z: number }[]
  RADAR: { distance: number }[]
}

export default function DataAcquisition({ sensors, locationId }: DataAcquisitionProps) {
  const router = useRouter()
  const [selectedSensor, setSelectedSensor] = useState<number | null>(null)
  const [sensorType, setSensorType] = useState<string>('')
  const [numDataPoints, setNumDataPoints] = useState<number>(100)
  const [fileName, setFileName] = useState<string>('')
  const [isAcquiring, setIsAcquiring] = useState(false)
  const [sensorData, setSensorData] = useState<any[]>([])
  const [acquisitionInterval, setAcquisitionInterval] = useState<NodeJS.Timeout | null>(null)

  // Update sensor type when sensor selection changes
  useEffect(() => {
    if (selectedSensor) {
      const sensor = sensors.find(s => s.id === selectedSensor)
      setSensorType(sensor?.type || '')
    } else {
      setSensorType('')
    }
  }, [selectedSensor, sensors])

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (acquisitionInterval) {
        clearInterval(acquisitionInterval)
      }
    }
  }, [acquisitionInterval])

  const simulateSensorReading = (type: string): any => {
    switch (type) {
      case 'LD':
        return Math.random() * 5 // 0-5V
      case 'ACCELEROMETER':
        return {
          x: (Math.random() - 0.5) * 4, // ±2g
          y: (Math.random() - 0.5) * 4,
          z: (Math.random() - 0.5) * 4,
        }
      case 'RADAR':
        return Math.random() * 10 // 0-10m
      default:
        return 0
    }
  }

  const handleStartAcquisition = async () => {
    if (!selectedSensor || !sensorType || isAcquiring) return

    setIsAcquiring(true)
    setSensorData([])

    // Simulate data collection
    const interval = setInterval(() => {
      setSensorData(prev => {
        if (prev.length >= numDataPoints) {
          clearInterval(interval)
          setIsAcquiring(false)
          handleDataUpload(prev)
          return prev
        }
        return [...prev, simulateSensorReading(sensorType)]
      })
    }, 100) // Collect data every 100ms

    setAcquisitionInterval(interval)
  }

  const handleDataUpload = async (data: any[]) => {
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
          data,
          fileName: fileName || defaultFileName,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to upload data')
      }

      // Clear the file name after successful upload
      setFileName('')
      // Force an immediate refresh
      router.refresh()
    } catch (error) {
      console.error('Error uploading data:', error)
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
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Enter file name"
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
      </div>
    </div>
  )
}
