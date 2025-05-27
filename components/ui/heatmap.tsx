import React from 'react';
import { cn } from '@/lib/utils';

interface HeatMapProps {
  data: number[][] | null;
  className?: string;
}

export function HeatMap({ data, className }: HeatMapProps) {
  if (!data) return null;

  const getColor = (value: number) => {
    // Normalize value to 0-1 range and map to color
    const normalized = Math.max(0, Math.min(1, value)); // Ensure value is between 0 and 1
    const hue = Math.round(240 * (1 - normalized)); // Map value to hue (blue for low, red for high)
    const saturation = 80 + (normalized * 20); // Increase saturation for more vibrant colors
    const lightness = 40 + (normalized * 10); // Adjust lightness to make changes more visible
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  // Rotate the data 90 degrees to display horizontally
  const rotatedData: number[][] = data[0].map((_, colIndex) => 
    data.map(row => row[colIndex])
  );

  return (
    <div className={cn("relative", className)}>
      <div className="absolute inset-0 flex flex-row">
        {rotatedData.map((row, rowIndex) => (
          <div key={rowIndex} className="flex flex-col">
            {row.map((value, colIndex) => (
              <div
                key={colIndex}
                className="h-2 w-2 border border-gray-300"
                style={{
                  backgroundColor: getColor(value),
                  transition: 'background-color 0.1s ease', // Add smooth transition
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
