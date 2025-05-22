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

interface FFTPlotProps {
  data: any[];
  sensorType: string;
}

// Compute FFT for the given data
function computeFFT(data: number[]): { frequencies: number[]; amplitudes: number[] } {
  // Ensure we have a power of 2 length for FFT
  const nextPowerOf2 = Math.pow(2, Math.ceil(Math.log2(data.length)));
  const paddedData = [...data];
  while (paddedData.length < nextPowerOf2) {
    paddedData.push(0);
  }

  // Apply FFT
  const fft = new Float32Array(nextPowerOf2 * 2);
  for (let i = 0; i < paddedData.length; i++) {
    fft[i * 2] = paddedData[i];
    fft[i * 2 + 1] = 0; // Imaginary part
  }

  // Perform in-place FFT
  const n = nextPowerOf2;
  for (let i = 0; i < Math.log2(n); i++) {
    const step = Math.pow(2, i);
    const halfStep = step / 2;
    
    for (let j = 0; j < n; j += step * 2) {
      for (let k = 0; k < step; k++) {
        const evenReal = fft[(j + k) * 2];
        const evenImag = fft[(j + k) * 2 + 1];
        const oddReal = fft[(j + k + step) * 2];
        const oddImag = fft[(j + k + step) * 2 + 1];
        
        const angle = -Math.PI * k / step;
        const cosAngle = Math.cos(angle);
        const sinAngle = Math.sin(angle);
        
        fft[(j + k) * 2] = evenReal + (cosAngle * oddReal - sinAngle * oddImag);
        fft[(j + k) * 2 + 1] = evenImag + (sinAngle * oddReal + cosAngle * oddImag);
        fft[(j + k + step) * 2] = evenReal - (cosAngle * oddReal - sinAngle * oddImag);
        fft[(j + k + step) * 2 + 1] = evenImag - (sinAngle * oddReal + cosAngle * oddImag);
      }
    }
  }

  // Calculate frequencies and amplitudes
  const frequencies: number[] = [];
  const amplitudes: number[] = [];
  const samplingRate = 1 / (data[1]?.time - data[0]?.time || 1); // Calculate sampling rate from time difference

  for (let i = 0; i < n / 2; i++) {
    const real = fft[i * 2];
    const imag = fft[i * 2 + 1];
    const amplitude = Math.sqrt(real * real + imag * imag) / n;
    const frequency = (i * samplingRate) / n;

    frequencies.push(frequency);
    amplitudes.push(amplitude);
  }

  return { frequencies, amplitudes };
}

export default function FFTPlot({ data, sensorType }: FFTPlotProps) {
  // Extract radar values and compute FFT
  const radarValues = data
    .filter(d => d.radar !== null && d.radar !== undefined)
    .map(d => Number(d.radar));

  const { frequencies, amplitudes } = computeFFT(radarValues);

  const chartData = {
    labels: frequencies.map(f => f.toFixed(2)),
    datasets: [
      {
        label: 'FFT Amplitude',
        data: amplitudes,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Radar Signal Frequency Analysis',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `Frequency: ${context.label} Hz, Amplitude: ${context.parsed.y.toFixed(6)}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Frequency (Hz)',
        },
        ticks: {
          maxTicksLimit: 10
        }
      },
      y: {
        title: {
          display: true,
          text: 'Amplitude',
        },
      },
    },
  };

  return <Line data={chartData} options={chartOptions} />;
}