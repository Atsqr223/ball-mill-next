import { useState } from 'react';
import YouTubeEmbed from './YouTubeEmbed';
import DataAcquisition from './DataAcquisition';
import DataAnalysis from './DataAnalysis';

interface LocationCardProps {
  location: {
    id: number;
    name: string;
    youtubeStreamId: string;
  };
}

export default function LocationCard({ location }: LocationCardProps) {
  const [activeTab, setActiveTab] = useState<'stream' | 'acquisition' | 'analysis'>('stream');

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h2 className="text-xl font-semibold">{location.name}</h2>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b dark:border-gray-700">
        <button
          className={`flex-1 py-2 px-4 ${
            activeTab === 'stream'
              ? 'bg-blue-500 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          onClick={() => setActiveTab('stream')}
        >
          Live Stream
        </button>
        <button
          className={`flex-1 py-2 px-4 ${
            activeTab === 'acquisition'
              ? 'bg-blue-500 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          onClick={() => setActiveTab('acquisition')}
        >
          Data Acquisition
        </button>
        <button
          className={`flex-1 py-2 px-4 ${
            activeTab === 'analysis'
              ? 'bg-blue-500 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
      </div>

      {/* Content Area */}
      <div className="p-4">
        {activeTab === 'stream' && (
          <div className="aspect-video">
            <YouTubeEmbed videoId={location.youtubeStreamId} />
          </div>
        )}
        {activeTab === 'acquisition' && (
          <DataAcquisition locationId={location.id} />
        )}
        {activeTab === 'analysis' && (
          <DataAnalysis locationId={location.id} />
        )}
      </div>
    </div>
  );
} 