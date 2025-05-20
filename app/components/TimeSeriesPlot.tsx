'use client';

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

interface TimeSeriesPlotProps {
  times: number[];
  data: (number | null)[];
  label: string;
  color: string;
}

export default function TimeSeriesPlot({ times, data, label, color }: TimeSeriesPlotProps) {
  // Debug logging
  console.log('TimeSeriesPlot props:', { times, data, label, color });

  // Ensure we have valid data
  if (!times?.length || !data?.length) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No data available for plotting
      </div>
    );
  }

  const chartData = {
    labels: times.map(t => t.toFixed(6)),
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: color + '20', // Add transparency
        tension: 0.1,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${label}: ${context.parsed.y?.toFixed(6)}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time (s)',
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          callback: function(value: any) {
            return Number(value).toFixed(3);
          }
        }
      },
      y: {
        title: {
          display: true,
          text: label,
        },
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return Number(value).toFixed(3);
          }
        }
      },
    },
  };

  return (
    <div className="h-64 w-full bg-white p-4 rounded-lg shadow">
      <Line data={chartData} options={options} />
    </div>
  );
} 