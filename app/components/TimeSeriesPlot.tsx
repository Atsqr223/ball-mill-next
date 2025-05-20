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
  console.log('TimeSeriesPlot props:', { 
    times: times.slice(0, 5), 
    data: data.slice(0, 5), 
    label, 
    color 
  });

  // Ensure we have valid data
  if (!times?.length || !data?.length) {
    console.log('No data available for plotting');
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No data available for plotting
      </div>
    );
  }

  // Create pairs of time and data values, filtering out null values
  const validData = times.map((time, index) => ({
    time,
    value: data[index]
  })).filter(item => item.value !== null);

  if (validData.length === 0) {
    console.log('No valid data points after filtering');
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No valid data points available
      </div>
    );
  }

  const chartData = {
    labels: validData.map(item => item.time.toString()),
    datasets: [
      {
        label,
        data: validData.map(item => item.value),
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
            return Number(value).toFixed(6);
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
            return Number(value).toFixed(6);
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