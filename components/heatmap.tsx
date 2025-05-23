'use client';

import React, { useEffect, useRef } from 'react';

interface HeatmapProps {
  data: number[][];
}

export const Heatmap: React.FC<HeatmapProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container || !data.length) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Calculate dimensions to maintain square pixels
    const containerWidth = container.clientWidth;
    const pixelWidth = containerWidth / data[0].length;
    const pixelHeight = pixelWidth; // Make pixels square
    const totalHeight = pixelHeight * data.length;

    // Set canvas size
    canvas.width = containerWidth;
    canvas.height = totalHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate cell sizes
    const cellWidth = canvas.width / data[0].length;
    const cellHeight = cellWidth; // Make cells square

    // Draw heatmap
    for (let y = 0; y < data.length; y++) {
      for (let x = 0; x < data[y].length; x++) {
        const value = data[y][x];
        
        // Create gradient from blue to red
        const r = Math.round(value * 255);
        const b = Math.round((1 - value) * 255);
        const g = 0;
        
        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
        ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
      }
    }
  }, [data]);

  return (
    <div ref={containerRef} className="w-full overflow-auto">
      <canvas
        ref={canvasRef}
        className="w-full"
        style={{ aspectRatio: `${data[0]?.length || 1}/${data.length || 1}` }}
      />
    </div>
  );
}; 
