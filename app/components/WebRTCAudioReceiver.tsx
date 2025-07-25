"use client";
import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";
import { HeatMap } from "../../components/ui/heatmap";

const SIGNALING_SERVER = "ws://20.163.22.17:65505";
// Dynamically import HeatMap to avoid SSR issues
// const HeatMap = dynamic(() => import("./ui/heatmap"), { ssr: false });

type AudioMode = "raw" | "processed";

export default function WebRTCAudioReceiver() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [status, setStatus] = useState("Idle");
  const [socketId, setSocketId] = useState<string | null>(null);
  const [heatmapData, setHeatmapData] = useState<number[][] | null>(null);
  const [selectedPixel, setSelectedPixel] = useState<{ x: number; y: number } | null>(null);
  const [audioMode, setAudioMode] = useState<AudioMode>("processed");
  const heatmapChannelRef = useRef<RTCDataChannel | null>(null);

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

        peerConnection.ondatachannel = (event) => {
          if (event.channel.label === "heatmap") {
            const channel = event.channel;
            heatmapChannelRef.current = channel;
            channel.onmessage = (e) => {
              try {
                const data = JSON.parse(e.data);
                if (data.heatmap) {
                  setHeatmapData(data.heatmap);
                }
              } catch (err) {}
            };
            channel.onopen = () => {
              setStatus((s) => s + " | Heatmap channel open");
            };
            channel.onclose = () => {
              setStatus((s) => s + " | Heatmap channel closed");
            };
          }
        };
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
    }
  }, [selectedPixel, audioMode]);

  // Handler for pixel click
  const handlePixelClick = (x: number, y: number) => {
    setSelectedPixel({ x, y });
  };

  return (
    <div style={{ padding: 16, border: "1px solid #ccc", borderRadius: 8, margin: 16 }}>
      <h3>WebRTC Audio Receiver</h3>
      <p>Status: {status}</p>
      <p>Socket ID: {socketId}</p>
      <audio ref={audioRef} controls autoPlay />
      <div style={{ marginTop: 24 }}>
        <h4>Live Heatmap</h4>
        {heatmapData ? (
          <HeatMap data={heatmapData} onPixelClick={handlePixelClick} selectedPixels={selectedPixel ? [selectedPixel] : []} />
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