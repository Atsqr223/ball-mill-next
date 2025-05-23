'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Heatmap } from "@/components/heatmap";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/components/ui/use-toast";
import Image from "next/image";
import { AlertCircle } from "lucide-react";

interface ValveState {
  index: number;
  isOpen: boolean;
}

interface HeatmapData {
  heatmap: number[][];
}

export default function PipelinePage() {
  const [connected, setConnected] = useState(false);
  const [piIp, setPiIp] = useState('');
  const [valveStates, setValveStates] = useState([false, false, false]);
  const [heatmapData, setHeatmapData] = useState<number[][]>([]);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const { toast } = useToast();

  const connectToPi = async () => {
    try {
      const response = await fetch(`http://${piIp}:5000/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ piIp }),
      });

      if (!response.ok) {
        throw new Error("Failed to connect");
      }

      const data = await response.json();
      if (data.status === "connected") {
        setConnected(true);
        toast({
          title: "Connected",
          description: "Successfully connected to Raspberry Pi",
        });
      }
    } catch (error) {
      toast({
        title: "Connection Error",
        description: `Failed to connect to Raspberry Pi at ${piIp}. Make sure the server is running and accessible.`,
        variant: "destructive",
      });
    }
  };

  const disconnectFromPi = async () => {
    try {
      const response = await fetch(`http://${piIp}:5000/disconnect`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to disconnect");
      }

      setConnected(false);
      setHeatmapData([]);
      toast({
        title: "Disconnected",
        description: "Successfully disconnected from Raspberry Pi",
      });
    } catch (error) {
      toast({
        title: "Disconnection Error",
        description: "Failed to disconnect from Raspberry Pi",
        variant: "destructive",
      });
    }
  };

  const toggleValve = async (index: number) => {
    if (!connected) return;

    try {
      const newState = !valveStates[index];
      const response = await fetch(`http://${piIp}:5000/valve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          valveIndex: index,
          state: newState,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to control valve");
      }

      setValveStates((prev) =>
        prev.map((valve, i) =>
          i === index ? newState : valve
        )
      );

      toast({
        title: `Valve ${index + 1} ${newState ? "Opened" : "Closed"}`,
        description: `Successfully ${newState ? "opened" : "closed"} valve ${index + 1}`,
      });
    } catch (error) {
      toast({
        title: "Valve Control Error",
        description: "Failed to control valve",
        variant: "destructive",
      });
    }
  };

  const fetchHeatmapData = async () => {
    if (!connected) return;

    try {
      const response = await fetch(`http://${piIp}:5000/heatmap`);
      if (!response.ok) {
        throw new Error("Failed to fetch heatmap data");
      }
      const data = await response.json();
      setHeatmapData(data.heatmap);
    } catch (error) {
      console.error("Error fetching heatmap data:", error);
    }
  };

  const switchMode = async (mode: 'live' | 'pickle') => {
    try {
      const response = await fetch(`http://${piIp}:5000/mode`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode }),
      });

      if (!response.ok) {
        throw new Error('Failed to switch mode');
      }

      const data = await response.json();
      setIsLiveMode(mode === 'live');
      toast({
        title: "Mode Changed",
        description: `Switched to ${mode} mode`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to switch mode",
        variant: "destructive",
      });
    }
  };

  // Add back the useEffect for periodic heatmap updates
  useEffect(() => {
    if (connected) {
      const interval = setInterval(fetchHeatmapData, 100);
      return () => clearInterval(interval);
    }
  }, [connected, piIp]); // Added piIp as dependency since it's used in fetchHeatmapData

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Pipeline Leakage Detection</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col space-y-4">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={piIp}
                  onChange={(e) => setPiIp(e.target.value)}
                  placeholder="Raspberry Pi IP"
                  className="flex-1 p-2 border rounded"
                />
                <Button onClick={connected ? disconnectFromPi : connectToPi}>
                  {connected ? 'Disconnect' : 'Connect'}
                </Button>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  onClick={() => switchMode('live')}
                  variant={isLiveMode ? "default" : "outline"}
                  disabled={!connected}
                >
                  Live Mode
                </Button>
                <Button
                  onClick={() => switchMode('pickle')}
                  variant={!isLiveMode ? "default" : "outline"}
                  disabled={!connected}
                >
                  Pickle Mode
                </Button>
              </div>

              {connected && (
                <div className="grid grid-cols-3 gap-2">
                  {[0, 1, 2].map((index) => (
                    <Button
                      key={index}
                      onClick={() => toggleValve(index)}
                      variant={valveStates[index] ? "default" : "outline"}
                    >
                      Valve {index + 1}
                    </Button>
                  ))}
                </div>
              )}

              {connected && (
                <div className="mt-4">
                  <img
                    src={valveStates.some(state => state) ? 
                      `/pipe_leakage/pipe_leak_${valveStates.findIndex(state => state) + 1}.png` : 
                      '/pipe_leakage/pipe_default.png'}
                    alt="Pipeline Status"
                    className="w-full h-auto"
                  />
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <h2 className="text-xl font-semibold mb-4">Acoustics Guided Localization</h2>
            {connected ? (
              <div className="h-[400px]">
                {heatmapData.length > 0 ? (
                  <Heatmap data={heatmapData} />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">Waiting for heatmap data...</p>
                  </div>
                )}
              </div>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Not Connected</AlertTitle>
                <AlertDescription>
                  Please connect to the Raspberry Pi to view the heatmap.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
