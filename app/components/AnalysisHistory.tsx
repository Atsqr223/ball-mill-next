'use client';

import { useState } from 'react';
import { Line } from 'react-chartjs-2';
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

interface Analysis {
  session: {
    id: number;
    numDataPoints: number;
    startTime: string;
    endTime: string | null;
    status: string;
  };
  data: Array<{
    value: number;
    timestamp: string;
  }>;
}

interface AnalysisHistoryProps {
  analyses: Analysis[];
}

export default function AnalysisHistory({ analyses }: AnalysisHistoryProps) {
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);

  if (analyses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 text-center">
        <p className="text-gray-500">No analysis history available</p>
      </div>
    );
  }

  const chartData = selectedAnalysis
    ? {
        labels: selectedAnalysis.data.map((d) =>
          new Date(d.timestamp).toLocaleTimeString()
        ),
        datasets: [
          {
            label: 'Sensor Data',
            data: selectedAnalysis.data.map((d) => d.value),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
        ],
      }
    : null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {analyses.map((analysis) => (
          <button
            key={analysis.session.id}
            onClick={() => setSelectedAnalysis(analysis)}
            className={`p-4 rounded-lg text-left transition-colors ${
              selectedAnalysis?.session.id === analysis.session.id
                ? 'bg-blue-50 border-2 border-blue-500'
                : 'bg-white border border-gray-200 hover:border-blue-300'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-medium">
                  Session #{analysis.session.id}
                </h3>
                <p className="text-sm text-gray-500">
                  {new Date(analysis.session.startTime).toLocaleString()}
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
            <div className="text-sm text-gray-600">
              <p>Data points: {analysis.session.numDataPoints}</p>
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
          </button>
        ))}
      </div>

      {selectedAnalysis && chartData && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            Analysis Results - Session #{selectedAnalysis.session.id}
          </h3>
          <div className="h-80">
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                  title: {
                    display: true,
                    text: 'Sensor Data Over Time',
                  },
                },
              }}
            />
          </div>
          {selectedAnalysis.data[0]?.analysisResults && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Analysis Results:</h4>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-auto">
                {JSON.stringify(selectedAnalysis.data[0].analysisResults, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 
