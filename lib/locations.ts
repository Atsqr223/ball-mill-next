export interface Sensor {
  id: number;
  type: 'Radar' | 'Mic' | 'Acceleration' | 'LD';
  name: string;
  status: 'active' | 'inactive';
}

export interface Location {
  id: number;
  name: string;
  youtubeStreamId: string;
  status: 'active' | 'inactive';
  sensors: Sensor[];
}

export const locations: Location[] = [
  {
    id: 1,
    name: 'TCSRI',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 1, type: 'Radar', name: 'Radar Sensor 1', status: 'active' },
      { id: 2, type: 'Mic', name: 'Microphone 1', status: 'active' },
      { id: 3, type: 'Acceleration', name: 'Accelerometer 1', status: 'active' },
      { id: 4, type: 'LD', name: 'LD Sensor 1', status: 'active' },
    ],
  },
  {
    id: 2,
    name: 'IITKGP',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 5, type: 'Radar', name: 'Radar Sensor 2', status: 'active' },
      { id: 6, type: 'Mic', name: 'Microphone 2', status: 'active' },
      { id: 7, type: 'Acceleration', name: 'Accelerometer 2', status: 'active' },
      { id: 8, type: 'LD', name: 'LD Sensor 2', status: 'active' },
    ],
  },
  {
    id: 3,
    name: 'TCS',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 9, type: 'Radar', name: 'Radar Sensor 3', status: 'active' },
      { id: 10, type: 'Mic', name: 'Microphone 3', status: 'active' },
      { id: 11, type: 'Acceleration', name: 'Accelerometer 3', status: 'active' },
      { id: 12, type: 'LD', name: 'LD Sensor 3', status: 'active' },
    ],
  },
]; 
