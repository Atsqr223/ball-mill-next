'use client'

import { useState } from 'react';

interface YouTubeEmbedProps {
  videoId: string;
}

export default function YouTubeEmbed({ videoId }: YouTubeEmbedProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  if (!isPlaying) {
    return (
      <div className="aspect-video bg-black rounded-lg overflow-hidden relative cursor-pointer" onClick={() => setIsPlaying(true)}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-white/10 hover:bg-white/20 rounded-full p-4 backdrop-blur-sm transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="white" className="w-12 h-12">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347c-.75.412-1.667-.13-1.667-.986V5.653z" />
            </svg>
          </div>
        </div>
        <div className="absolute bottom-4 left-4 text-white text-lg font-medium">
          Click to play video
        </div>
      </div>
    );
  }

  return (
    <iframe
      className="w-full h-full"
      src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`}
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    />
  );

}
