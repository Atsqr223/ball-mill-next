'use client';

import { useState } from 'react';
import { Line } from 'react-chartjs-2';
import Link from 'next/link';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface SensorReading {
  id: number;
  timestamp: string;
  value?: number;
  voltage?: number;
  x?: number;
  y?: number;
  z?: number;
  distance?: number;
  unit?: string;
}

interface Analysis {
  session: {
    id: number;
    numDataPoints: number;
    startTime: string;
    endTime: string | null;
    status: string;
    sensorType: string;
    metadata: Record<string, any>;
    fileName: string | null;
  };
  data: SensorReading[];
}

interface AnalysisHistoryProps {
  analyses: Analysis[];
  locationId: number;
}

export default function AnalysisHistory({ analyses, locationId }: AnalysisHistoryProps) {
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);

  if (analyses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 text-center">
        <p className="text-gray-500">No analysis history available</p>
      </div>
    );
  }

  const getChartData = (analysis: Analysis) => {
    const labels = analysis.data.map((d) =>
      new Date(d.timestamp).toLocaleTimeString()
    );

    switch (analysis.session.sensorType) {
      case 'LD':
        return {
          labels,
          datasets: [
            {
              label: 'Voltage (V)',
              data: analysis.data.map((d) => d.voltage),
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
          ],
        };
      case 'ACCELEROMETER':
        return {
          labels,
          datasets: [
            {
              label: 'X Acceleration (m/s²)',
              data: analysis.data.map((d) => d.x),
              borderColor: 'rgb(255, 99, 132)',
              tension: 0.1,
            },
            {
              label: 'Y Acceleration (m/s²)',
              data: analysis.data.map((d) => d.y),
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
            {
              label: 'Z Acceleration (m/s²)',
              data: analysis.data.map((d) => d.z),
              borderColor: 'rgb(153, 102, 255)',
              tension: 0.1,
            },
          ],
        };
      case 'RADAR':
        return {
          labels,
          datasets: [
            {
              label: 'Distance (m)',
              data: analysis.data.map((d) => d.distance),
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
            },
          ],
        };
      default:
        return null;
    }
  };

  const chartData = selectedAnalysis ? getChartData(selectedAnalysis) : null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {analyses.map((analysis) => (
          <Link
            key={analysis.session.id}
            href={`/locations/${locationId}/acquisitions/${analysis.session.id}`}
            className="block"
          >
            <div className="p-4 rounded-lg bg-white border border-gray-200 hover:border-blue-300 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-medium">
                    {analysis.session.fileName || `Session #${analysis.session.id}`}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {new Date(analysis.session.startTime).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Sensor Type: {analysis.session.sensorType}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    analysis.session.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {analysis.session.status}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                <p>{analysis.session.numDataPoints} data points</p>
                {analysis.session.endTime && (
                  <p>
                    Duration:{' '}
                    {Math.round(
                      (new Date(analysis.session.endTime).getTime() -
                        new Date(analysis.session.startTime).getTime()) /
                        1000
                    )}{' '}
                    seconds
                  </p>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {selectedAnalysis && chartData && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">
            Session #{selectedAnalysis.session.id} Data
          </h3>
          <div className="h-96">
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  title: {
                    display: true,
                    text: `${selectedAnalysis.session.sensorType} Sensor Data`,
                  },
                },
                scales: {
                  x: {
                    title: {
                      display: true,
                      text: 'Time',
                    },
                  },
                  y: {
                    title: {
                      display: true,
                      text: selectedAnalysis.data[0]?.unit || 'Value',
                    },
                  },
                },
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
