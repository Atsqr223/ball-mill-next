import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface DataAnalysisProps {
  locationId: number;
}

interface AcquisitionSession {
  id: number;
  startTime: string;
  numDataPoints: number;
  status: string;
}

interface AnalysisData {
  dataPoints: { timestamp: string; value: number }[];
  analysisResults: {
    mean: number;
    std: number;
    fft: { frequency: number; magnitude: number }[];
  };
}

export default function DataAnalysis({ locationId }: DataAnalysisProps) {
  const [sessions, setSessions] = useState<AcquisitionSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [activeChart, setActiveChart] = useState<'time' | 'fft'>('time');

  useEffect(() => {
    fetchSessions();
  }, [locationId]);

  useEffect(() => {
    if (selectedSession) {
      fetchAnalysisData(selectedSession);
    }
  }, [selectedSession]);

  const fetchSessions = async () => {
    try {
      const response = await fetch(`/api/analysis/sessions/${locationId}`);
      const data = await response.json();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const fetchAnalysisData = async (sessionId: number) => {
    try {
      const response = await fetch(`/api/analysis/data/${sessionId}`);
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Error fetching analysis data:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2">Select Session</h3>
        <select
          className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          value={selectedSession || ''}
          onChange={(e) => setSelectedSession(Number(e.target.value))}
        >
          <option value="">Select a session...</option>
          {sessions.map((session) => (
            <option key={session.id} value={session.id}>
              {new Date(session.startTime).toLocaleString()} - {session.numDataPoints} points
            </option>
          ))}
        </select>
      </div>

      {selectedSession && analysisData && (
        <>
          <div className="flex space-x-4">
            <button
              className={`flex-1 p-2 rounded ${
                activeChart === 'time'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700'
              }`}
              onClick={() => setActiveChart('time')}
            >
              Time Series
            </button>
            <button
              className={`flex-1 p-2 rounded ${
                activeChart === 'fft'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700'
              }`}
              onClick={() => setActiveChart('fft')}
            >
              FFT Analysis
            </button>
          </div>

          <div className="h-80">
            {activeChart === 'time' ? (
              <Plot
                data={[
                  {
                    x: analysisData.dataPoints.map(p => p.timestamp),
                    y: analysisData.dataPoints.map(p => p.value),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Sensor Data',
                  },
                ]}
                layout={{
                  title: { text: 'Time Series Data' },
                  xaxis: { title: { text: 'Time' } },
                  yaxis: { title: { text: 'Value' } },
                  margin: { t: 30 },
                }}
                useResizeHandler
                style={{ width: '100%', height: '100%' }}
              />
            ) : (
              <Plot
                data={[
                  {
                    x: analysisData.analysisResults.fft.map(p => p.frequency),
                    y: analysisData.analysisResults.fft.map(p => p.magnitude),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'FFT',
                  },
                ]}
                layout={{
                  title: { text: 'FFT Analysis' },
                  xaxis: { title: { text: 'Frequency (Hz)' } },
                  yaxis: { title: { text: 'Magnitude' } },
                  margin: { t: 30 },
                }}
                useResizeHandler
                style={{ width: '100%', height: '100%' }}
              />
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded">
              <h4 className="font-medium mb-2">Mean</h4>
              <p>{analysisData.analysisResults.mean.toFixed(4)}</p>
            </div>
            <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded">
              <h4 className="font-medium mb-2">Standard Deviation</h4>
              <p>{analysisData.analysisResults.std.toFixed(4)}</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
} 