import React from 'react';
import { cn } from '@/lib/utils';

interface HeatMapProps {
  data: number[][] | null;
  className?: string;
}

export function HeatMap({ data, className }: HeatMapProps) {
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

  return (
    <div className={cn("relative", className)}>
      <div className="absolute inset-0 flex flex-col">
        {transposedData.map((row, rowIndex) => (
          <div key={rowIndex} className="flex flex-row">
            {row.map((value, colIndex) => (
              <div
                key={colIndex}
                className="h-4 w-4 border border-gray-300"
                style={{
                  backgroundColor: getColor(value),
                  transition: 'background-color 0.1s ease',
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
