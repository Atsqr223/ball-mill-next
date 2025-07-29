"use client";
import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";
import { HeatMap } from "../../components/ui/heatmap";

const SIGNALING_SERVER = "ws://20.163.22.17:65505";
// Dynamically import HeatMap to avoid SSR issues
// const HeatMap = dynamic(() => import("./ui/heatmap"), { ssr: false });

type AudioMode = "raw" | "processed";

// Define PIXEL_COLORS and WINDOW_SIZE at the top
const PIXEL_COLORS = [
  'rgb(255, 99, 132)',   // Red
  'rgb(54, 162, 235)',   // Blue
  'rgb(255, 206, 86)',   // Yellow
  'rgb(75, 192, 192)',   // Green
  'rgb(153, 102, 255)',  // Purple
  'rgb(255, 159, 64)',   // Orange
];
const WINDOW_SIZE = 1000;

const getAnglesFromPixels = (x: number, y: number): { theta: number; phi: number } | null => {
  // This should match the implementation in your Python code
  // For now, we'll use a simple mapping that assumes a 2D plane
  // You'll need to adjust this to match your actual implementation
  const width = 50; // Adjust based on your heatmap dimensions
  const height = 5;
  
  // Simple mapping from pixel to spherical coordinates
  const theta = (x / width) * 2 * Math.PI;  // 0 to 2π
  const phi = (y / height) * Math.PI;        // 0 to π
  
  return { theta, phi };
};

const applySpatialFilter = (audioData: number[][], theta: number, phi: number): { raw: number[]; filtered: number[] } => {
  // Convert to numpy-like array for easier manipulation
  const numSamples = audioData.length;
  const numChannels = audioData[0].length;
  
  // Create a weight matrix for each channel based on angles
  const weights = new Array(numChannels).fill(0);
  for (let i = 0; i < numChannels; i++) {
    // Calculate weight based on channel position
    const channelAngle = 2 * Math.PI * i / numChannels;
    weights[i] = Math.cos(theta - channelAngle) * Math.sin(phi);
  }
  
  // Normalize weights
  const weightSum = weights.reduce((sum, w) => sum + Math.abs(w), 0);
  const normalizedWeights = weightSum !== 0 ? weights.map(w => w / weightSum) : weights;
  
  // Apply weights to each channel and sum
  const filteredAudio = new Array(numSamples).fill(0);
  for (let i = 0; i < numSamples; i++) {
    for (let c = 0; c < numChannels; c++) {
      filteredAudio[i] += audioData[i][c] * normalizedWeights[c];
    }
  }
  
  // Normalize the output
  const maxAmplitude = Math.max(...filteredAudio.map(Math.abs));
  const normalizedAudio = maxAmplitude > 0 
    ? filteredAudio.map(sample => sample / maxAmplitude)
    : filteredAudio;
  
  // Apply low-pass filter (simplified implementation)
  // In a real implementation, you might want to use a proper filter library
  const lpfCutoff = 1000; // Hz
  const samplingRate = 48000; // Hz
  const rc = 1.0 / (2 * Math.PI * lpfCutoff);
  const dt = 1.0 / samplingRate;
  const alpha = dt / (rc + dt);
  
  const lowPassAudio = new Array(normalizedAudio.length);
  lowPassAudio[0] = normalizedAudio[0];
  for (let i = 1; i < normalizedAudio.length; i++) {
    lowPassAudio[i] = alpha * normalizedAudio[i] + (1 - alpha) * lowPassAudio[i - 1];
  }
  
  return {
    raw: normalizedAudio,
    filtered: lowPassAudio
  };
};

export default function WebRTCAudioReceiver() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [status, setStatus] = useState("Idle");
  const [socketId, setSocketId] = useState<string | null>(null);
  const [heatmapData, setHeatmapData] = useState<number[][] | null>(null);
  const [selectedPixel, setSelectedPixel] = useState<{ x: number; y: number } | null>(null);
  const [audioMode, setAudioMode] = useState<AudioMode>("processed");
  const heatmapChannelRef = useRef<RTCDataChannel | null>(null);
  const [pixelAudioData, setPixelAudioData] = useState<{ x: number; y: number; raw: Float32Array; filtered: Float32Array } | null>(null);
  const [sessionEnded, setSessionEnded] = useState(false);

  useEffect(() => {
    const socket = io(SIGNALING_SERVER);
    let peerConnection: RTCPeerConnection | null = null;
    let remoteStream: MediaStream | null = null;
    let senderId: string | null = null;

    socket.on("connect", () => {
      setStatus("Connected to signaling server");
      socket.emit("ready");
    });

    socket.on("your-id", (id: string) => {
      setSocketId(id);
    });

    socket.on("signal", async ({ from, message }) => {
      senderId = from;
      if (!peerConnection) {
        peerConnection = new RTCPeerConnection({
          iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            {
              urls: 'turn:openrelay.metered.ca:80',
              username: 'openrelayproject',
              credential: 'openrelayproject'
            }
          ],
        });

        peerConnection.ondatachannel = (event) => {
          const channel = event.channel;

          if (channel.label === "heatmap") {
            heatmapChannelRef.current = channel;

            channel.onmessage = (e) => {
              try {
                const data = JSON.parse(e.data);
                console.log('Received data channel message:', data);

                if (data.heatmap) {
                  console.log('Setting heatmap data');
                  setHeatmapData(data.heatmap);
                }

                // Handle raw audio data for spatial filtering
                if (data.type === "audioData" && Array.isArray(data.channels)) {
                  console.log('Received multi-channel audio data with', data.channels.length, 'channels and', data.channels[0]?.length || 0, 'samples');

                  if (selectedPixel) {
                    console.log('Processing audio data for pixel:', selectedPixel.x, selectedPixel.y);
                    const angles = getAnglesFromPixels(selectedPixel.x, selectedPixel.y);
                    if (angles) {
                      const { theta, phi } = angles;
                      const processed = applySpatialFilter(data.channels, theta, phi);
                      console.log('Processed audio data - raw length:', processed.raw.length, 'filtered length:', processed.filtered.length);

                      // Ensure we have valid data before updating state
                      if (processed.raw.length > 0 && processed.filtered.length > 0) {
                        setPixelAudioData({
                          x: selectedPixel.x,
                          y: selectedPixel.y,
                          raw: new Float32Array(processed.raw),
                          filtered: new Float32Array(processed.filtered)
                        });
                      } else {
                        console.warn('Received empty audio data');
                      }
                    }
                  }
                }

                // Handle pre-processed audio buffer
                if (data.type === "audioBuffer" && data.x !== undefined && data.y !== undefined) {
                  console.log('Received pre-processed audio buffer for pixel:', data.x, data.y, 
                    'raw length:', data.raw?.length || 0, 
                    'filtered length:', data.filtered?.length || 0);
                  if ((data.raw?.length || 0) > 0 && (data.filtered?.length || 0) > 0) {
                    // Only set audio data if it matches the currently selected pixel
                    if (selectedPixel && data.x === selectedPixel.x && data.y === selectedPixel.y) {
                      setPixelAudioData({
                        x: data.x,
                        y: data.y,
                        raw: new Float32Array(data.raw || []),
                        filtered: new Float32Array(data.filtered || [])
                      });
                      setSessionEnded(true);
                    } else {
                      console.warn('Received audio buffer for non-selected pixel:', data.x, data.y);
                    }
                  } else {
                    console.warn('Received empty audio buffer data');
                  }
                }
              } catch (err) {
                console.error('Error processing data channel message:', err);
              }
            };

            channel.onopen = () => {
              setStatus("Heatmap data channel connected");
              console.log('Heatmap data channel opened');
            };

            channel.onclose = () => {
              setStatus(prev => prev + " | Heatmap channel closed");
              console.log('Heatmap data channel closed');
            };

            channel.onerror = (error) => {
              console.error('Data channel error:', error);
              setStatus(prev => prev + ` | Error: ${error.toString()}`);
            };
          }
        };

        remoteStream = new MediaStream();
        peerConnection.ontrack = (event) => {
          remoteStream!.addTrack(event.track);
          if (audioRef.current) {
            audioRef.current.srcObject = remoteStream;
            audioRef.current.play();
          }
        };

        peerConnection.onicecandidate = (event) => {
          if (event.candidate && senderId) {
            socket.emit("signal", { target: senderId, message: { candidate: event.candidate } });
          }
        };

        setStatus("Created RTCPeerConnection");
      }

      if (message.sdp) {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
        if (message.sdp.type === "answer") {
          setStatus("WebRTC connection established");
        } else if (message.sdp.type === "offer") {
          const answer = await peerConnection.createAnswer();
          await peerConnection.setLocalDescription(answer);
          socket.emit("signal", { target: senderId, message: { sdp: peerConnection.localDescription } });
        }
      } else if (message.candidate) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
      }
    });

    return () => {
      socket.disconnect();
      if (peerConnection) peerConnection.close();
    };
  }, []);

  // Send pixel selection/mode to sender
  useEffect(() => {
    if (selectedPixel && heatmapChannelRef.current && heatmapChannelRef.current.readyState === "open") {
      const msg = JSON.stringify({ type: "pixel", x: selectedPixel.x, y: selectedPixel.y, mode: audioMode });
      heatmapChannelRef.current.send(msg);
      // Also request audio data for this pixel
      // const audioMsg = JSON.stringify({ type: 'getAudioData', x: selectedPixel.x, y: selectedPixel.y });
      // heatmapChannelRef.current.send(audioMsg);
      setPixelAudioData(null);
      console.log('Sent pixel selection and audio data request (effect):', msg, audioMsg);
    }
  }, [selectedPixel, audioMode]);

  // Handler for pixel click
  const handlePixelClick = (x: number, y: number) => {
    console.log('Pixel clicked:', x, y);
    setSelectedPixel({ x, y });
    setPixelAudioData(null); // Clear previous audio data
    // Send pixel selection/mode to sender
    if (heatmapChannelRef.current?.readyState === 'open') {
      const msg = JSON.stringify({ type: 'pixel', x, y, mode: audioMode });
      heatmapChannelRef.current.send(msg);
      // Add a short delay before requesting audio data
      setTimeout(() => {
        if (heatmapChannelRef.current?.readyState === 'open') {
          const audioMsg = JSON.stringify({ type: 'getAudioData', x, y });
          heatmapChannelRef.current.send(audioMsg);
          console.log('Sent audio data request (delayed):', audioMsg);
        }
      }, 100); // 100ms delay
      console.log('Sent pixel selection:', msg);
    }
  };

  // Play the buffer using Web Audio API
  const playBuffer = (buffer: number[] | Float32Array) => {
    if (!buffer || buffer.length === 0) return;
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const audioBuffer = audioContext.createBuffer(1, buffer.length, 44100);
    const arr = buffer instanceof Float32Array ? buffer : new Float32Array(buffer);
    audioBuffer.copyToChannel(arr, 0);
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
    source.onended = () => {
      audioContext.close();
    };
  };

  // Handler for play button
  const handlePlay = (type: 'raw' | 'filtered') => {
    if (!pixelAudioData) return;
    const arr = type === 'filtered' ? pixelAudioData.filtered : pixelAudioData.raw;
    playBuffer(arr);
  };

  return (
    <div style={{ padding: 16, border: "1px solid #ccc", borderRadius: 8, margin: 16 }}>
      <h3>WebRTC Audio Receiver</h3>
      <p>Status: {status}</p>
      <p>Socket ID: {socketId}</p>
      <audio ref={audioRef} controls autoPlay style={{ display: 'none' }} />
      <div style={{ marginTop: 24 }}>
        {sessionEnded && (
          <div style={{ color: 'red', fontWeight: 'bold', marginBottom: 16 }}>
            Session ended. Please refresh the page to start a new session.
          </div>
        )}
        <h4>Live Heatmap</h4>
        {heatmapData ? (
          <HeatMap
            data={heatmapData}
            onPixelClick={handlePixelClick}
            selectedPixels={selectedPixel ? [{
              x: selectedPixel.x,
              y: selectedPixel.y,
              color: "black", // Use first color for now
              audioData: pixelAudioData ? {
                raw: Array.from(pixelAudioData.raw),
                filtered: Array.from(pixelAudioData.filtered)
              } : null,
              isPlaying: false,
              windowSize: WINDOW_SIZE
            }] : []}
            onPlay={handlePlay}
          />
        ) : (
          <p>Waiting for heatmap data...</p>
        )}
        <div style={{ marginTop: 16 }}>
          <label>
            <input
              type="radio"
              name="audioMode"
              value="processed"
              checked={audioMode === "processed"}
              onChange={() => setAudioMode("processed")}
            />
            Processed Audio
          </label>
          <label style={{ marginLeft: 16 }}>
            <input
              type="radio"
              name="audioMode"
              value="raw"
              checked={audioMode === "raw"}
              onChange={() => setAudioMode("raw")}
            />
            Raw Audio
          </label>
        </div>
        {selectedPixel && (
          <div style={{ marginTop: 8 }}>
            <b>Selected Pixel:</b> ({selectedPixel.x}, {selectedPixel.y})
          </div>
        )}
      </div>
    </div>
  );
}