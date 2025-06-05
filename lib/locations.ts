export interface Sensor {
  id: number;
  type: 'Radar' | 'Mic' | 'Acceleration' | 'LD';
  name: string;
  status: 'active' | 'inactive';
}

export type LocationType = 'ball-mill' | 'pipeline' | 'plc' | 'something';

export interface Location {
  id: number;
  name: string;
  youtubeStreamId: string;
  status: 'active' | 'inactive';
  sensors: Sensor[];
  type: LocationType;
}

export const locations: Location[] = [
  {
    id: 1,
    name: 'TCSRI',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 1, type: 'Radar', name: 'Radar Sensor 1', status: 'active' },
      { id: 2, type: 'Acceleration', name: 'Accelerometer 1', status: 'active' },
      { id: 3, type: 'LD', name: 'LD Sensor 1', status: 'active' },
      { id: 4, type: 'Mic', name: 'Microphone 1', status: 'active' },
    ],
    type: 'ball-mill',
  },
  {
    id: 2,
    name: 'IITKGP',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 5, type: 'Radar', name: 'Radar Sensor 2', status: 'active' },
      { id: 6, type: 'Acceleration', name: 'Accelerometer 2', status: 'active' },
      { id: 7, type: 'LD', name: 'LD Sensor 2', status: 'active' },
      { id: 8, type: 'Mic', name: 'Microphone 2', status: 'active' },
    ],
    type: 'ball-mill',
  },
  {
    id: 3,
    name: 'TCS',
    youtubeStreamId: 'jfKfPfyJRdk',  // Sample YouTube live stream
    status: 'active',
    sensors: [
      { id: 9, type: 'Radar', name: 'Radar Sensor 3', status: 'active' },
      { id: 10, type: 'Acceleration', name: 'Accelerometer 3', status: 'active' },
      { id: 11, type: 'LD', name: 'LD Sensor 3', status: 'active' },
      { id: 12, type: 'Mic', name: 'Microphone 3', status: 'active' },
    ],
    type: 'ball-mill',
  },
  // Pipeline Locations
  {
    id: 4,
    name: 'TCSRI - Pipeline',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      { id: 13, type: 'Radar', name: 'Pipeline Radar 1', status: 'active' },
      { id: 14, type: 'Mic', name: 'Pipeline Mic 1', status: 'active' },
    ],
    type: 'pipeline',
  },
  {
    id: 5,
    name: 'IITKGP - Pipeline',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      { id: 15, type: 'Radar', name: 'Pipeline Radar 2', status: 'active' },
      { id: 16, type: 'Mic', name: 'Pipeline Mic 2', status: 'active' },
    ],
    type: 'pipeline',
  },
  // PLC Locations
  {
    id: 6,
    name: 'TCSRI - PLC',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      // Define PLC specific sensors or copy Ball Mill's for now
      { id: 17, type: 'Acceleration', name: 'PLC Accel 1', status: 'active' },
      { id: 18, type: 'LD', name: 'PLC LD 1', status: 'active' },
    ],
    type: 'plc',
  },
  {
    id: 7,
    name: 'IITKGP - PLC',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      { id: 19, type: 'Acceleration', name: 'PLC Accel 2', status: 'active' },
      { id: 20, type: 'LD', name: 'PLC LD 2', status: 'active' },
    ],
    type: 'plc',
  },
  // Something Locations
  {
    id: 8,
    name: 'TCSRI - Something',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      // Define 'Something' specific sensors or copy Ball Mill's for now
      { id: 21, type: 'Radar', name: 'Something Radar 1', status: 'active' },
      { id: 22, type: 'Mic', name: 'Something Mic 1', status: 'active' },
    ],
    type: 'something',
  },
  {
    id: 9,
    name: 'IITKGP - Something',
    youtubeStreamId: 'jfKfPfyJRdk', // Sample YouTube live stream, update as needed
    status: 'active',
    sensors: [
      { id: 23, type: 'Radar', name: 'Something Radar 2', status: 'active' },
      { id: 24, type: 'Mic', name: 'Something Mic 2', status: 'active' },
    ],
    type: 'something',
  },
]; 
