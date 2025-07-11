import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
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

// Colors for pixel selection
const PIXEL_COLORS = [
  'rgb(255, 99, 132)',   // Red
  'rgb(54, 162, 235)',   // Blue
  'rgb(255, 206, 86)',   // Yellow
  'rgb(75, 192, 192)',   // Green
  'rgb(153, 102, 255)',  // Purple
  'rgb(255, 159, 64)',   // Orange
];

interface SelectedPixel {
  x: number;
  y: number;
  color: string;
  audioData: {
    raw: number[];
    filtered: number[];
  } | null;
  isPlaying: boolean;
  windowSize?: number;  // Size of the rolling window
}

interface HeatMapProps {
  data: number[][] | null;
  className?: string;
}

export function HeatMap({ data, className }: HeatMapProps) {
  const [selectedPixels, setSelectedPixels] = useState<SelectedPixel[]>([]);
  const [error, setError] = useState<string | null>(null);
  const WINDOW_SIZE = 1000;  // Show 1000 points in the window
  // Add scroll positions for each selected pixel
  const [scrollPositions, setScrollPositions] = useState<{ [key: string]: number }>({});

  // Update audio data for selected pixels
  useEffect(() => {
    if (selectedPixels.length === 0) return;

    const updateAudioData = async () => {
      try {
        const updatedPixels = await Promise.all(
          selectedPixels.map(async (pixel) => {
            // Only update if the pixel is still selected
            if (!selectedPixels.some(p => p.x === pixel.x && p.y === pixel.y)) {
              return pixel;
            }

            const response = await fetch('/api/pipeline/playback/select', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ x: pixel.x, y: pixel.y }),
            });

            if (!response.ok) {
              throw new Error('Failed to update audio data');
            }

            const data = await response.json();
            return {
              ...pixel,
              audioData: data.audio_data,
              windowSize: WINDOW_SIZE
            };
          })
        );

        // Only update state if we still have selected pixels
        if (selectedPixels.length > 0) {
          setSelectedPixels(updatedPixels);
        }
      } catch (err) {
        console.error('Error updating audio data:', err);
      }
    };

    // Update every 100ms
    const interval = setInterval(updateAudioData, 100);
    return () => clearInterval(interval);
  }, [selectedPixels]);

  // Update scroll positions if new pixels are added
  useEffect(() => {
    setScrollPositions((prev) => {
      const updated = { ...prev };
      selectedPixels.forEach((pixel) => {
        const key = `${pixel.x},${pixel.y}`;
        if (!(key in updated)) {
          updated[key] = 0; // Start at the beginning
        }
      });
      // Remove scroll positions for deselected pixels
      Object.keys(updated).forEach((key) => {
        if (!selectedPixels.some(p => `${p.x},${p.y}` === key)) {
          delete updated[key];
        }
      });
      return updated;
    });
  }, [selectedPixels]);

  if (!data) return null;

  // Flatten the data to compute min and max
  const flatValues = data.flat();
  const min = Math.min(...flatValues);
  const max = Math.max(...flatValues);

  const getColor = (value: number) => {
    const normalized = Math.max(0, Math.min(1, (value - min) / (max - min || 1))); // Avoid divide by zero

    let hue;
    if (normalized <= 0.5) {
      // Blue (240) to Yellow (60)
      hue = 240 - (normalized / 0.5) * (240 - 60);
    } else {
      // Yellow (60) to Red (0)
      hue = 60 - ((normalized - 0.5) / 0.5) * 60;
    }

    return `hsl(${hue}, 100%, 50%)`;
  };

  // Transpose the data to get horizontal heatmap
  const transposedData: number[][] = data[0].map((_, colIndex) =>
    data.map(row => row[colIndex])
  );

  const handlePixelClick = async (x: number, y: number) => {
    try {
      setError(null);
      
      // Check if pixel is already selected
      const existingPixelIndex = selectedPixels.findIndex(p => p.x === x && p.y === y);
      if (existingPixelIndex !== -1) {
        // Deselect the pixel
        const response = await fetch('/api/pipeline/playback/deselect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ x, y }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error || 'Failed to deselect pixel');
        }

        // Remove the pixel from the selected pixels array
        setSelectedPixels(prevPixels => prevPixels.filter((_, index) => index !== existingPixelIndex));
        return;
      }

      // Select new pixel
      const response = await fetch('/api/pipeline/playback/select', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ x, y }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 503) {
          // Server not ready or buffer empty - retry after a delay
          console.log('Server not ready, retrying in 1 second...');
          setTimeout(() => handlePixelClick(x, y), 1000);
          return;
        }
        // Show the actual error message from the server
        throw new Error(data.error || 'Failed to select pixel');
      }

      // Add the new pixel to the selected pixels array
      setSelectedPixels(prevPixels => {
        // Check if this pixel is already in the array (shouldn't happen, but just in case)
        if (prevPixels.some(p => p.x === x && p.y === y)) {
          return prevPixels;
        }
        
        const colorIndex = prevPixels.length % PIXEL_COLORS.length;
        return [
          ...prevPixels,
          {
            x,
            y,
            color: PIXEL_COLORS[colorIndex],
            audioData: data.audio_data,
            isPlaying: false,
            windowSize: WINDOW_SIZE
          }
        ];
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to select pixel';
      setError(errorMessage);
      console.error('Pixel selection error:', errorMessage);
    }
  };

  const handlePlayback = async (pixelIndex: number) => {
    try {
      setError(null);
      const pixel = selectedPixels[pixelIndex];
      
      const response = await fetch('/api/pipeline/playback/play', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          x: pixel.x, 
          y: pixel.y,
          use_filtered: true  // Use filtered signal for playback
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to control playback');
      }

      const data = await response.json();
      const newPixels = [...selectedPixels];
      newPixels[pixelIndex] = {
        ...pixel,
        isPlaying: data.status === 'playing'
      };
      setSelectedPixels(newPixels);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to control playback');
    }
  };

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <div className="relative">
        {transposedData.map((row, rowIndex) => (
          <div key={rowIndex} className="flex flex-row">
            {row.map((value, colIndex) => {
              const selectedPixel = selectedPixels.find(p => p.x === colIndex && p.y === rowIndex);
              return (
                <div
                  key={colIndex}
                  className={cn(
                    "h-4 w-4 border border-gray-300 cursor-pointer transition-all",
                    selectedPixel && "ring-2"
                  )}
                  style={{
                    backgroundColor: getColor(value),
                    transition: 'background-color 0.1s ease',
                    borderColor: selectedPixel?.color || 'transparent',
                  }}
                  onClick={() => handlePixelClick(colIndex, rowIndex)}
                />
              );
            })}
          </div>
        ))}
      </div>

      {error && (
        <div className="text-red-500">
          {error}
        </div>
      )}

      {selectedPixels.length > 0 && (
        <div className="max-h-[600px] overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedPixels.map((pixel, index) => {
              const key = `${pixel.x},${pixel.y}`;
              const audioLength = pixel.audioData ? pixel.audioData.raw.length : 0;
              const maxScroll = Math.max(0, audioLength - WINDOW_SIZE);
              const scroll = scrollPositions[key] || 0;
              // Clamp scroll
              const clampedScroll = Math.max(0, Math.min(scroll, maxScroll));
              return (
                <div key={key} className="bg-white rounded-lg shadow-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold" style={{ color: pixel.color }}>
                      Pixel ({pixel.x}, {pixel.y})
                    </h3>
                    <Button
                      onClick={() => handlePlayback(index)}
                      variant={pixel.isPlaying ? "destructive" : "default"}
                      style={{ borderColor: pixel.color }}
                    >
                      {pixel.isPlaying ? "Stop" : "Play"}
                    </Button>
                  </div>
                  {pixel.audioData && (
                    <div className="space-y-4">
                      <div className="h-48">
                        <Line
                          data={{
                            labels: Array.from({ length: WINDOW_SIZE }, (_, i) => i + clampedScroll),
                            datasets: [
                              {
                                label: 'Raw Signal',
                                data: pixel.audioData.raw.slice(clampedScroll, clampedScroll + WINDOW_SIZE),
                                borderColor: pixel.color,
                                tension: 0.1,
                                borderWidth: 1,
                                pointRadius: 0,
                              },
                              {
                                label: 'Low-Pass Filtered',
                                data: pixel.audioData.filtered.slice(clampedScroll, clampedScroll + WINDOW_SIZE),
                                borderColor: 'rgb(0, 0, 0)',
                                tension: 0.1,
                                borderWidth: 2,
                                pointRadius: 0,
                              }
                            ],
                          }}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            animation: {
                              duration: 0,
                            },
                            plugins: {
                              legend: {
                                display: true,
                                position: 'top',
                              },
                              title: {
                                display: true,
                                text: 'Time Series (Scrollable Window)',
                              },
                            },
                            scales: {
                              y: {
                                beginAtZero: true,
                                min: -1,
                                max: 1,
                              },
                              x: {
                                display: false,
                              }
                            },
                          }}
                        />
                      </div>
                      {/* Slider for scrolling */}
                      {audioLength > WINDOW_SIZE && (
                        <input
                          type="range"
                          min={0}
                          max={maxScroll}
                          value={clampedScroll}
                          onChange={e => {
                            const newScroll = parseInt(e.target.value, 10);
                            setScrollPositions(pos => ({ ...pos, [key]: newScroll }));
                          }}
                          className="w-full mt-2"
                        />
                      )}
                      <div className="text-xs text-gray-500 text-right">
                        Showing samples {clampedScroll + 1} - {Math.min(clampedScroll + WINDOW_SIZE, audioLength)} of {audioLength}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
