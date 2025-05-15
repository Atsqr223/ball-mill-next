'use client'

import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface BallMillVisualizationProps {
  locationId: string
}

export default function BallMillVisualization({ locationId }: BallMillVisualizationProps) {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    // Fetch initial data
    fetchData()
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [locationId])

  const fetchData = async () => {
    try {
      const response = await fetch(`/api/ball-mill-data/${locationId}`)
      const { x, y, z } = await response.json()
      
      setData([
        {
          type: 'scatter3d',
          mode: 'markers',
          x,
          y,
          z,
          marker: {
            size: 5,
            color: 'blue',
            opacity: 0.8
          }
        },
        {
          type: 'mesh3d',
          x: generateCylinderX(),
          y: generateCylinderY(),
          z: generateCylinderZ(),
          opacity: 0.3,
          color: 'gray'
        }
      ])
    } catch (error) {
      console.error('Error fetching ball mill data:', error)
    }
  }

  // Helper functions to generate cylinder mesh
  const generateCylinderX = () => {
    // Implementation here
    return []
  }

  const generateCylinderY = () => {
    // Implementation here
    return []
  }

  const generateCylinderZ = () => {
    // Implementation here
    return []
  }

  return (
    <div className="w-full h-[400px]">
      <Plot
        data={data}
        layout={{
          title: 'Ball Mill Visualization',
          autosize: true,
          scene: {
            aspectmode: 'cube',
            camera: {
              eye: { x: 1.5, y: 1.5, z: 1.5 }
            }
          },
          margin: { t: 30, b: 0, l: 0, r: 0 }
        }}
        useResizeHandler
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  )
} 