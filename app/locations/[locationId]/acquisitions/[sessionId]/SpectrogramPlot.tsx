'use client';

import { useEffect, useRef } from 'react';

interface SensorData {
  id: number;
  sensorTime: string;
  radar?: number;
  accelerationX?: number;
  accelerationY?: number;
  accelerationZ?: number;
  distance?: number;
}

interface SpectrogramPlotProps {
  data: SensorData[];
  sensorType: string;
}

function computeSpectrogram(data: number[], windowSize: number, overlap: number) {
  const hop = windowSize - overlap;
  const numWindows = Math.floor((data.length - overlap) / hop);
  const spectrogram: number[][] = [];

  // Hann window function
  const hannWindow = new Float32Array(windowSize);
  for (let i = 0; i < windowSize; i++) {
    hannWindow[i] = 0.5 * (1 - Math.cos((2 * Math.PI * i) / (windowSize - 1)));
  }

  for (let i = 0; i < numWindows; i++) {
    const start = i * hop;
    let segment = data.slice(start, start + windowSize);
    
    // Ensure segment is fully populated
    if (segment.length < windowSize) {
      const padding = new Array(windowSize - segment.length).fill(0);
      segment = [...segment, ...padding];
    }
    
    // Apply window function
    const windowed = segment.map((x, j) => (x || 0) * hannWindow[j]);
    
    // Pad to power of 2 if needed
    const paddedLength = Math.pow(2, Math.ceil(Math.log2(windowSize)));
    const padded = [...windowed];
    while (padded.length < paddedLength) {
      padded.push(0);
    }

    // Compute FFT
    const real = new Float32Array(paddedLength);
    const imag = new Float32Array(paddedLength);
    for (let j = 0; j < paddedLength; j++) {
      real[j] = padded[j] || 0;
      imag[j] = 0;
    }

    // In-place FFT
    for (let size = 2; size <= paddedLength; size *= 2) {
      const halfSize = size / 2;
      const angleDelta = -2 * Math.PI / size;
      
      for (let start = 0; start < paddedLength; start += size) {
        let angle = 0;
        for (let j = start; j < start + halfSize; j++) {
          const cos = Math.cos(angle);
          const sin = Math.sin(angle);
          
          const k = j + halfSize;
          const tReal = real[k] * cos - imag[k] * sin;
          const tImag = real[k] * sin + imag[k] * cos;
          
          real[k] = real[j] - tReal;
          imag[k] = imag[j] - tImag;
          real[j] += tReal;
          imag[j] += tImag;
          
          angle += angleDelta;
        }
      }
    }

    // Compute magnitudes for this window
    const magnitudes = new Array(paddedLength / 2);
    for (let j = 0; j < paddedLength / 2; j++) {
      magnitudes[j] = Math.sqrt(real[j] * real[j] + imag[j] * imag[j]) / paddedLength;
    }

    spectrogram.push(magnitudes);

    if (i === 0) {
      console.log('First window magnitudes:', magnitudes);
      console.log('Max value in first window:', Math.max(...magnitudes));
    }
  }

  return spectrogram;
}

export default function SpectrogramPlot({ data, sensorType }: SpectrogramPlotProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !data || data.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    console.log('Data length:', data.length);

    // Clear canvas with a dark background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Extract sensor values based on sensor type
    let values: number[];
    if (sensorType === 'LD') {
      values = data.map(d => d.distance || 0);
    } else if (sensorType === 'ACCELEROMETER') {
      // Use the magnitude of acceleration
      values = data.map(d => 
        Math.sqrt(
          Math.pow(d.accelerationX || 0, 2) + 
          Math.pow(d.accelerationY || 0, 2) + 
          Math.pow(d.accelerationZ || 0, 2)
        )
      );
    } else {
      return;
    }

    // Debug logging
    console.log('Processing sensor data:', {
      sensorType,
      dataLength: values.length,
      sampleValues: values.slice(0, 5)
    });

    // Compute spectrogram
    const windowSize = 256; // Adjust based on your needs
    const overlap = Math.floor(windowSize * 0.75); // 75% overlap
    const spectrogram = computeSpectrogram(values, windowSize, overlap);

    // Debug logging
    console.log('Spectrogram computation result:', {
      windowSize,
      overlap,
      spectrogramDimensions: {
        time: spectrogram.length,
        frequency: spectrogram[0]?.length || 0
      },
      maxValue: Math.max(...spectrogram.flat())
    });

    // Draw spectrogram
    const padding = { left: 50, bottom: 30 };
    const plotWidth = canvas.width - padding.left - 60; // Account for legend
    const plotHeight = canvas.height - padding.bottom;

    // Create a temporary canvas for the spectrogram
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = plotWidth;
    tempCanvas.height = plotHeight;
    const tempCtx = tempCanvas.getContext('2d');
    if (!tempCtx) return;

    const imageData = tempCtx.createImageData(plotWidth, plotHeight);

    // Scale spectrogram to plot dimensions
    const timeScale = plotWidth / spectrogram.length;
    const freqScale = plotHeight / (windowSize / 2);

    // Calculate max value for normalization
    let maxVal = Number.EPSILON; // Avoid division by zero
    for (const row of spectrogram) {
      for (const val of row) {
        const absVal = Math.abs(val);
        maxVal = Math.max(maxVal, absVal);
      }
    }
    
    // Use log scale for better dynamic range
    const logMax = Math.log10(maxVal + 1);

    // Draw pixels
      for (let t = 0; t < spectrogram.length; t++) {
        for (let f = 0; f < windowSize / 2; f++) {
          const x = Math.floor(t * timeScale);
          const y = plotHeight - Math.floor(f * freqScale) - 1; // Flip y-axis

          if (x >= 0 && x < plotWidth && y >= 0 && y < plotHeight) {
            const magnitude = Math.abs(spectrogram[t][f]);
            const logNorm = Math.log10(magnitude + 1) / logMax;
            // Ensure value is between 0 and 1
            const normalizedValue = Math.max(0, Math.min(1, logNorm));

            // Enhanced colormap: dark blue to cyan to yellow to red
             const value = Math.pow(normalizedValue, 0.7); // Gamma correction for better contrast
             let r, g, b;
             
             if (value < 0.33) {
               // Dark blue to cyan
               const t = value * 3;
               r = 0;
               g = Math.floor(255 * t);
               b = Math.floor(255 * (0.5 + 0.5 * t));
             } else if (value < 0.66) {
               // Cyan to yellow
               const t = (value - 0.33) * 3;
               r = Math.floor(255 * t);
               g = 255;
               b = Math.floor(255 * (1 - t));
             } else {
               // Yellow to red
               const t = (value - 0.66) * 3;
               r = 255;
               g = Math.floor(255 * (1 - t));
               b = 0;
             }
             
             // Ensure color values are within valid range
             r = Math.max(0, Math.min(255, r));
             g = Math.max(0, Math.min(255, g));
             b = Math.max(0, Math.min(255, b));

            const idx = (y * plotWidth + x) * 4;
            if (idx >= 0 && idx < imageData.data.length - 3) {
              imageData.data[idx] = r;
              imageData.data[idx + 1] = g;
              imageData.data[idx + 2] = b;
              imageData.data[idx + 3] = 255;
            }
          }
        }
    }

    // Put the image data on the temporary canvas
    tempCtx.putImageData(imageData, 0, 0);

    // Clear the main canvas and set background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw the spectrogram from the temporary canvas
    ctx.drawImage(tempCanvas, padding.left, 0);
    
    // Add axis labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // Y-axis (Frequency)
    ctx.save();
    ctx.translate(15, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Frequency (Hz)', 0, 0);
    ctx.restore();
    
    // X-axis (Time)
    ctx.fillText('Time', canvas.width / 2, canvas.height - 5);
    
    // Calculate actual sample rate from timestamps
    const timestamps = data.map(d => new Date(d.sensorTime).getTime());
    const timeDiffs = timestamps.slice(1).map((t, i) => t - timestamps[i]);
    const avgTimeDiff = timeDiffs.reduce((a, b) => a + b, 0) / timeDiffs.length;
    const sampleRate = 1000 / avgTimeDiff; // Convert to Hz
    const maxFreq = sampleRate / 2; // Nyquist frequency

    // Add frequency scale on y-axis
    ctx.textAlign = 'right';
    for (let i = 0; i <= 4; i++) {
      const y = (canvas.height - padding.bottom) * (i / 4);
      const freq = (maxFreq * (4 - i) / 4).toFixed(1);
      ctx.fillText(`${freq}`, padding.left - 5, y + 4);
    }

    // Add time scale on x-axis
    const totalDuration = (timestamps[timestamps.length - 1] - timestamps[0]) / 1000; // in seconds
    ctx.textAlign = 'center';
    for (let i = 0; i <= 4; i++) {
      const x = padding.left + (canvas.width - padding.left) * (i / 4);
      const time = (totalDuration * i / 4).toFixed(1);
      ctx.fillText(`${time}s`, x, canvas.height - padding.bottom + 20);
    }

    // Add color legend
    const legendWidth = 20;
    const legendHeight = plotHeight * 0.7;
    const legendX = canvas.width - 40;
    const legendY = (canvas.height - legendHeight) / 2;

    // Draw legend gradient
    const legendGradient = ctx.createLinearGradient(0, legendY + legendHeight, 0, legendY);
    legendGradient.addColorStop(0, 'rgb(0, 0, 128)');   // Dark blue
    legendGradient.addColorStop(0.33, 'rgb(0, 255, 255)'); // Cyan
    legendGradient.addColorStop(0.66, 'rgb(255, 255, 0)'); // Yellow
    legendGradient.addColorStop(1, 'rgb(255, 0, 0)');   // Red

    ctx.fillStyle = legendGradient;
    ctx.fillRect(legendX, legendY, legendWidth, legendHeight);

    // Add legend border
    ctx.strokeStyle = '#ffffff';
    ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);

    // Add legend labels
    ctx.textAlign = 'right';
    ctx.fillStyle = '#ffffff';
    ctx.fillText('High', legendX - 5, legendY + 15);
    ctx.fillText('Low', legendX - 5, legendY + legendHeight - 5);
  }, [data, sensorType]);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        width={1100}
        height={500}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          backgroundColor: '#1a1a1a',
          borderRadius: '4px'
        }}
      />
    </div>
  );
}