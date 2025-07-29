'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import Image from 'next/image';
import { HeatMap } from '@/components/ui/heatmap';
import { cn } from '@/lib/utils';
import WebRTCAudioReceiver from '../components/WebRTCAudioReceiver';

export interface PipelineControlProps {
  youtubeStreamId?: string;
  pressure?: number | null;
}

export default function PipelineControl({ youtubeStreamId = 'jfKfPfyJRdk', pressure }: PipelineControlProps) {
  const [piIp, setPiIp] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [valveStates, setValveStates] = useState([false, false, false]);
  const [currentImage, setCurrentImage] = useState('/pipe_leakage/pipe_default.png');
  const [heatmapData, setHeatmapData] = useState(null);
  const [heatmapError, setHeatmapError] = useState<string | null>(null);
  const [isAudioServerRunning, setIsAudioServerRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [plcOutput, setPlcOutput] = useState(false);
  const [plcLoading, setPlcLoading] = useState(false);
  const [plcError, setPlcError] = useState<string | null>(null);
  const [pipeOverlayScale, setPipeOverlayScale] = useState(1.0); // Example: 1.0 = 100%
  const [pipeOverlayTranslate, setPipeOverlayTranslate] = useState({ x: 0, y: 0 }); // Example: { x: 0, y: 0 }
  const [heatmapTranslate, setHeatmapTranslate] = useState({ x: 0, y: 0 }); // Example: { x: 0, y: 0 }
  const [webRTCTranslate, setWebRTCTranslate] = useState({ x: 0, y: 0 });

  // Example: set initial values for testing
  useEffect(() => {
    setPipeOverlayScale(0.77);
    setPipeOverlayTranslate({ x: -210, y: -150 });
    setHeatmapTranslate({ x: 30, y: 182 });
    setWebRTCTranslate({ x: -3, y: 30 });
  }, []);

  // Check connection status periodically
  useEffect(() => {
    // if (!isConnected) return;

    // // Check pipeline status
    // const checkStatus = async () => {
    //   try {
    //     const response = await fetch('/api/pipeline/status');
    //     if (!response.ok) {
    //       setIsConnected(false);
    //       setError('Lost connection to server');
    //     }
    //   } catch (error) {
    //     setIsConnected(false);
    //     setError('Failed to check connection status');
    //   }
    // };
    // console.log('checking connection status');
    // Fetch heatmap data
    const fetchHeatmap = async () => {
      try {
        const response = await fetch(`/api/pipeline/heatmap?ts=${Date.now()}`, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Expires': '0',
          }
        });
        if (response.ok) {
          const data = await response.json();
          setHeatmapData(data.heatmap);
          setHeatmapError(null);
          setIsAudioServerRunning(true);
        } else {
          const errorData = await response.json();
          setHeatmapError(errorData.error || 'Audio server is not running');
          setHeatmapData(null);
          setIsAudioServerRunning(false);
        }
      } catch (error) {
        setHeatmapError('Audio server is not running');
        setHeatmapData(null);
        setIsAudioServerRunning(false);
        console.error('Heatmap fetch error:', error);
      }
    };

    // Set up intervals
    // const statusInterval = setInterval(checkStatus, 5000);
    const heatmapInterval = setInterval(fetchHeatmap, 1000); // Update heatmap every 50ms to match audio server's rate

    return () => {
      // clearInterval(statusInterval);
      clearInterval(heatmapInterval);
    };
  }, []);

  // Update image whenever valveStates changes
  useEffect(() => {
    setCurrentImage(getPipeLeakImage(valveStates));
  }, [valveStates]);

  // Helper function to map valveStates to the correct image
  function getPipeLeakImage(valveStates: boolean[]) {
    const open = valveStates
      .map((state, idx) => (state ? (idx + 1).toString() : ''))
      .filter(Boolean)
      .join('');
    if (!open) return '/pipe_leakage/pipe_default.png';
    if (open.length === 1) return `/pipe_leakage/pipe_leak_${open}.png`;
    return `/pipe_leakage/pipe_leak_${open.split('').sort().join('')}.png`;
  }

  const handleConnect = async () => {
    setError(null);
    try {
      const response = await fetch('/api/pipeline/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ piIp }),
      });

      if (response.ok) {
        setIsConnected(true);
        // Get initial valve states after connecting
        const statusResponse = await fetch('/api/pipeline/status');
        if (statusResponse.ok) {
          const data = await statusResponse.json();
          if (data.valveStates) {
            setValveStates(data.valveStates);
            // No need to setCurrentImage here, useEffect will handle it
          }
        }
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to connect to Raspberry Pi');
      }
    } catch (error) {
      setError('Failed to connect to Raspberry Pi');
    }
  };

  const handleDisconnect = async () => {
    setError(null);
    setIsDisconnecting(true);
    try {
      const response = await fetch('/api/pipeline/disconnect', {
        method: 'POST',
      });

      if (response.ok) {
        setIsConnected(false);
        setValveStates([false, false, false]); // Reset all valves
        // No need to setCurrentImage here, useEffect will handle it
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to disconnect from Raspberry Pi');
      }
    } catch (error) {
      setError('Failed to disconnect from Raspberry Pi');
    } finally {
      setIsDisconnecting(false);
    }
  };

  const toggleValve = async (index: number) => {
    // Allow toggling regardless of isConnected
    setError(null);

    // Update UI immediately for better responsiveness
    const newStates = [...valveStates];
    newStates[index] = !valveStates[index];
    setValveStates(newStates);
    
    // Update image based on valve state
    if (newStates[index]) {
      setCurrentImage(`/pipe_leakage/pipe_leak_${index + 1}.png`);
    } else {
      setCurrentImage('/pipe_leakage/pipe_default.png');
    }

    try {
      const response = await fetch('/api/pipeline/valve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          valveIndex: index,
          state: newStates[index]  // Use the new state we just set
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.valveStates) {
          // Update states from server response
          setValveStates(data.valveStates);
          // Update image based on server-confirmed valve states
          const openValveIndex = data.valveStates.findIndex((state: boolean) => state);
          if (openValveIndex !== -1) {
            setCurrentImage(`/pipe_leakage/pipe_leak_${openValveIndex + 1}.png`);
          } else {
            setCurrentImage('/pipe_leakage/pipe_default.png');
          }
        }
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to toggle valve');
        // Optionally, revert the UI state if backend fails
        // const revertStates = [...valveStates];
        // revertStates[index] = !newStates[index];
        // setValveStates(revertStates);
      }
    } catch (error) {
      setError('Failed to toggle valve');
      // Optionally, revert the UI state if backend fails
      // const revertStates = [...valveStates];
      // revertStates[index] = !newStates[index];
      // setValveStates(revertStates);
    }
  };

  const handlePlcToggle = async () => {
    setPlcLoading(true);
    setPlcError(null);
    try {
      const response = await fetch('/api/pipeline/plc-io', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: !plcOutput }),
      });
      const data = await response.json();
      if (response.ok && data.success) {
        setPlcOutput(!plcOutput);
      } else {
        setPlcError(data.error || 'Failed to set PLC output');
      }
    } catch (error: any) {
      setPlcError(error.message || 'Failed to set PLC output');
    } finally {
      setPlcLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Pipeline Control</h1>
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-3 h-3 rounded-full",
            isConnected ? "bg-green-500" : "bg-red-500"
          )} />
          <span className="text-sm text-muted-foreground">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
              </svg>
              Raspberry Pi Connection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="flex-1">
                <Label htmlFor="piIp" className="text-sm font-medium">Raspberry Pi IP Address</Label>
                <Input
                  id="piIp"
                  value={piIp}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPiIp(e.target.value)}
                  placeholder="e.g., 192.168.1.100 or 10.135.1.1"
                  disabled={isConnected}
                  className="mt-1"
                />
              </div>
              {isConnected ? (
                <Button 
                  onClick={handleDisconnect} 
                  disabled={isDisconnecting}
                  variant="destructive"
                  className="min-w-[120px]"
                >
                  {isDisconnecting ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Disconnecting...
                    </>
                  ) : 'Disconnect'}
                </Button>
              ) : (
                <Button 
                  onClick={handleConnect} 
                  disabled={!piIp || isConnected}
                  className="min-w-[120px]"
                >
                  Connect
                </Button>
              )}
            </div>
            {error && (
              <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {error}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Valve Control
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-6">
              {valveStates.map((state, index) => (
                <div key={index} className="flex flex-col items-center space-y-3">
                  <div className={cn(
                    "w-16 h-16 rounded-full flex items-center justify-center transition-colors",
                    state ? "bg-green-100" : "bg-gray-100"
                  )}>
                    <Switch
                      id={`valve${index}`}
                      checked={state}
                      onCheckedChange={() => toggleValve(index)}
                      className="scale-125"
                    />
                  </div>
                  <Label htmlFor={`valve${index}`} className="text-sm font-medium">
                    {['Left', 'Center', 'Right'][index]}
                  </Label>
                  <span className={cn(
                    "text-xs px-2 py-1 rounded-full",
                    state ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
                  )}>
                    {state ? "Open" : "Closed"}
                  </span>
                </div>
              ))}
            </div>
            {/* PLC Output Button */}
            <div className="flex flex-col items-center mt-8">
              <Button
                onClick={handlePlcToggle}
                disabled={plcLoading}
                variant={plcOutput ? 'default' : 'outline'}
                className="min-w-[180px]"
              >
                {plcLoading ? 'Switching...' : `Compressor: ${plcOutput ? 'ON' : 'OFF'}`}
              </Button>
              {plcError && (
                <p className="mt-2 text-sm text-red-500">{plcError}</p>
              )}
              {/* Pressure value box below compressor button */}
              <div className="mt-4 p-4 bg-gray-100 rounded shadow w-fit">
                <span className="font-semibold">Pressure: </span>
                <span className="text-xl">{pressure !== undefined && pressure !== null ? pressure.toFixed(2) : 'Loading...'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Pipeline Visualization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-video rounded-lg overflow-hidden border">
              {/* YouTube Live Video */}
              <iframe
                className="absolute inset-0 w-full h-full"
                src={`https://www.youtube.com/embed/${youtubeStreamId}?autoplay=1`}
                title="YouTube Live Stream"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 relative">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Acoustics Guided Localization
            </CardTitle>
          </CardHeader>
          <CardContent className="relative">
         {/*
            {!isAudioServerRunning && (
              <div className="bg-yellow-50 text-yellow-700 p-4 rounded-md mb-4 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                Audio server is not running. Please start the audio server to see the heatmap.
              </div>
            )}
            {heatmapError && (
              <div className="bg-red-50 text-red-500 p-4 rounded-md mb-4 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {heatmapError}
              </div>
            )}
        */}
            <div className="relative aspect-video rounded-lg overflow-hidden border">
              {/* WebRTC Overlay - Positioned absolutely to overlap */}
              <div
                className="absolute top-0 left-0 w-full h-full z-10"
                style={{
                  transform: `translate(${webRTCTranslate.x}px, ${webRTCTranslate.y}px)`
                }}
              >
                <WebRTCAudioReceiver />
              </div>
              
              {/* Heatmap with adjustable translation */}
              <div
                className="w-full h-full absolute top-0 left-0 z-30 pointer-events-none"
                style={{
                  transform: `translate(${heatmapTranslate.x}px, ${heatmapTranslate.y}px)`
                }}
              >
                <HeatMap
                  data={heatmapData}
                  className="w-full h-full"
                />
              </div>
              {/* Pipe image overlay with adjustable transform */}
              <div
                className="w-full h-full absolute top-0 left-0 z-20 pointer-events-none"
                style={{
                  transform: `scale(${pipeOverlayScale}) translate(${pipeOverlayTranslate.x}px, ${pipeOverlayTranslate.y}px)`,
                  mixBlendMode: 'multiply',
                }}
              >
                <Image
                  src={currentImage}
                  alt="Pipeline"
                  fill
                  className="object-contain opacity-40"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
