'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import Image from 'next/image';

export default function PipelineControl() {
  const [piIp, setPiIp] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [valveStates, setValveStates] = useState([false, false, false]);
  const [currentImage, setCurrentImage] = useState('/pipe_leakage/pipe_default.png');
  const [error, setError] = useState<string | null>(null);
  const [isDisconnecting, setIsDisconnecting] = useState(false);

  // Check connection status periodically
  useEffect(() => {
    if (!isConnected) return;

    const checkStatus = async () => {
      try {
        const response = await fetch('/api/pipeline/status');
        if (!response.ok) {
          setIsConnected(false);
          setError('Lost connection to server');
        }
      } catch (error) {
        setIsConnected(false);
        setError('Failed to check connection status');
      }
    };

    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, [isConnected]);

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
            // Update image based on valve states
            const openValveIndex = data.valveStates.findIndex((state: boolean) => state);
            if (openValveIndex !== -1) {
              setCurrentImage(`/pipe_leakage/pipe_leak_${openValveIndex + 1}.png`);
            } else {
              setCurrentImage('/pipe_leakage/pipe_default.png');
            }
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
        setCurrentImage('/pipe_leakage/pipe_default.png');
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
    if (!isConnected) return;
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
        // Revert the state if the request failed
        const revertStates = [...valveStates];
        revertStates[index] = !newStates[index];
        setValveStates(revertStates);
        // Revert image if needed
        if (!revertStates[index]) {
          const otherValveOpen = revertStates.findIndex((state: boolean) => state);
          if (otherValveOpen !== -1) {
            setCurrentImage(`/pipe_leakage/pipe_leak_${otherValveOpen + 1}.png`);
          } else {
            setCurrentImage('/pipe_leakage/pipe_default.png');
          }
        }
      }
    } catch (error) {
      setError('Failed to toggle valve');
      // Revert the state if the request failed
      const revertStates = [...valveStates];
      revertStates[index] = !newStates[index];
      setValveStates(revertStates);
      // Revert image if needed
      if (!revertStates[index]) {
        const otherValveOpen = revertStates.findIndex((state: boolean) => state);
        if (otherValveOpen !== -1) {
          setCurrentImage(`/pipe_leakage/pipe_leak_${otherValveOpen + 1}.png`);
        } else {
          setCurrentImage('/pipe_leakage/pipe_default.png');
        }
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Pipeline Control</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Raspberry Pi Connection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <Label htmlFor="piIp">Raspberry Pi IP Address</Label>
              <Input
                id="piIp"
                value={piIp}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPiIp(e.target.value)}
                placeholder="e.g., 192.168.1.100"
                disabled={isConnected}
              />
            </div>
            {isConnected ? (
              <Button 
                onClick={handleDisconnect} 
                disabled={isDisconnecting}
                variant="destructive"
              >
                {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
              </Button>
            ) : (
              <Button 
                onClick={handleConnect} 
                disabled={!piIp || isConnected}
              >
                Connect
              </Button>
            )}
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-500">{error}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Valve Control</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              {[0, 1, 2].map((index) => (
                <div key={index} className="flex items-center justify-between">
                  <Label>Valve {index + 1}</Label>
                  <Switch
                    checked={valveStates[index]}
                    onCheckedChange={() => toggleValve(index)}
                    disabled={!isConnected}
                  />
                </div>
              ))}
            </div>
            <div className="relative h-[300px] w-full">
              <Image
                src={currentImage}
                alt="Pipeline Status"
                fill
                className="object-contain"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}