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

// Register Chart.js components
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
  data: any[];
  sensorType: string;
}

// Normalize sensor type to match schema
function normalizeSensorType(type: string): string {
  const normalized = type.toUpperCase();
  // Handle various sensor type formats
  if (normalized === 'AUDIO') return 'ACCELEROMETER';
  if (normalized === 'LASER_DISTANCE') return 'LD';
  return normalized;
}

export default function TimeSeriesPlot({ data, sensorType }: TimeSeriesPlotProps) {
  console.log('Raw data sample:', data.slice(0, 5));
  console.log('Original sensor type:', sensorType);

  const type = normalizeSensorType(sensorType);
  console.log('Normalized sensor type:', type);

  // Process data to ensure we have valid values
  const processedData = data.map(d => {
    let value = null;
    let accelerationY = null;
    let accelerationZ = null;

    // Log the raw values for debugging
    console.log('Processing data point:', {
      type,
      distance: d.distance,
      accelerationX: d.accelerationX,
      accelerationY: d.accelerationY,
      accelerationZ: d.accelerationZ,
      radar: d.radar,
      sensorTime: d.sensorTime
    });

    if (type === 'LD') {
      if (d.distance !== null && d.distance !== undefined) {
        value = Number(d.distance);
        console.log('LD sensor value:', value);
      }
    } else if (type === 'ACCELEROMETER' || type === 'ACCELERATION') {
      if (d.accelerationX !== null && d.accelerationX !== undefined) {
        value = Number(d.accelerationX);
      }
      if (d.accelerationY !== null && d.accelerationY !== undefined) {
        accelerationY = Number(d.accelerationY);
      }
      if (d.accelerationZ !== null && d.accelerationZ !== undefined) {
        accelerationZ = Number(d.accelerationZ);
      }
    } else if (type === 'RADAR') {
      if (d.radar !== null && d.radar !== undefined) {
        value = Number(d.radar);
      }
    }

    return {
      time: d.sensorTime ? Number(d.sensorTime) : null,
      value,
      accelerationY,
      accelerationZ,
    };
  }).filter(d => {
    const isValid = d.time !== null && (
      (type === 'LD' && d.value !== null) ||
      ((type === 'ACCELEROMETER' || type === 'ACCELERATION') && (d.value !== null || d.accelerationY !== null || d.accelerationZ !== null)) ||
      (type === 'RADAR' && d.value !== null)
    );
    if (!isValid) {
      console.log('Filtered out data point:', d);
    }
    return isValid;
  });

  console.log('Processed data sample:', processedData.slice(0, 5));
  console.log('Total processed data points:', processedData.length);

  // Create datasets based on sensor type
  const datasets = (type === 'ACCELEROMETER' || type === 'ACCELERATION') ? [
    {
      label: 'X Acceleration (m/s²)',
      data: processedData.map(d => d.value),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      tension: 0.1,
      pointRadius: 2,
      pointHoverRadius: 5,
    },
    {
      label: 'Y Acceleration (m/s²)',
      data: processedData.map(d => d.accelerationY),
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      tension: 0.1,
      pointRadius: 2,
      pointHoverRadius: 5,
    },
    {
      label: 'Z Acceleration (m/s²)',
      data: processedData.map(d => d.accelerationZ),
      borderColor: 'rgb(54, 162, 235)',
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      tension: 0.1,
      pointRadius: 2,
      pointHoverRadius: 5,
    }
  ] : [{
    label: type === 'LD' ? 'Distance (m)' :
           type === 'ACCELEROMETER' || type === 'ACCELERATION' ? 'Acceleration (m/s²)' :
           type === 'RADAR' ? 'Radar' : 'Value',
    data: processedData.map(d => d.value),
    borderColor: 'rgb(75, 192, 192)',
    backgroundColor: 'rgba(75, 192, 192, 0.5)',
    tension: 0.1,
    pointRadius: 2,
    pointHoverRadius: 5,
  }];

  const chartData = {
    labels: processedData.map(d => d.time?.toString() || ''),
    datasets,
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: `${type} Sensor Data`,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(6)}`;
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
          maxTicksLimit: 10
        }
      },
      y: {
        title: {
          display: true,
          text: type === 'LD' ? 'Distance (m)' :
                type === 'ACCELEROMETER' || type === 'ACCELERATION' ? 'Acceleration (m/s²)' :
                type === 'RADAR' ? 'Radar' : 'Value',
        },
      },
    },
  };

  return <Line data={chartData} options={chartOptions} />;
} 