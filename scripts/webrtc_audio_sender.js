// Node.js WebRTC Audio Sender
const wrtc = require('wrtc');
const io = require('socket.io-client');
const axios = require('axios');

const SIGNALING_SERVER = 'ws://20.163.22.17:65505';
const ROOM = 'audio-room';

const SAMPLE_RATE = 48000;
const FREQUENCY = 440;
const CHANNELS = 1;

const DAQ_SERVER = 'http://localhost:5002'; // Python DAQ microservice

// Top-level variable declarations for all timers and connections
let peerConnection = null;
let audioTimer = null;
let audioBufferInterval = null;
let heatmapInterval = null;
let heatmapChannel = null;
let audioSource = null;
let selectedPixel = null;
let audioMode = 'processed';

// Helper for spatial filtering (matches Python logic)
function getAnglesFromPixelsPipe(x, y) {
  const length_intervals = 50;
  const diameter_intervals = 5;
  const x_norm = (x / length_intervals) * 2 - 1;
  const y_norm = (y / diameter_intervals) * 2 - 1;
  const theta = Math.atan2(y_norm, x_norm);
  const radius = Math.sqrt(x_norm ** 2 + y_norm ** 2);
  const phi = Math.acos(Math.max(0, Math.min(1, radius)));
  return [theta, phi];
}

function spatialFilter(audioData, x, y) {
  // audioData: [samples][channels]
  const [theta, phi] = getAnglesFromPixelsPipe(x, y);
  const channels = audioData[0].length;
  // Create weights
  const weights = Array.from({ length: channels }, (_, i) => {
    const channel_angle = 2 * Math.PI * i / channels;
    return Math.cos(theta - channel_angle) * Math.sin(phi);
  });
  const weightSum = weights.reduce((a, b) => a + Math.abs(b), 0) || 1;
  const normWeights = weights.map(w => w / weightSum);
  // Apply weights and sum
  const filtered = audioData.map(row => row.reduce((sum, v, i) => sum + v * normWeights[i], 0));
  // Normalize
  const maxAbs = Math.max(...filtered.map(Math.abs)) || 1;
  return filtered.map(v => v / maxAbs);
}

function lowPassFilter(signal, sampleRate, cutoff = 1000, order = 4) {
  // Simple IIR low-pass filter (Butterworth, biquad)
  // For production, use a DSP lib. Here, use a basic moving average as a placeholder.
  const windowSize = Math.floor(sampleRate / cutoff);
  if (windowSize < 2) return signal;
  const filtered = [];
  for (let i = 0; i < signal.length; ++i) {
    let sum = 0;
    let count = 0;
    for (let j = Math.max(0, i - windowSize + 1); j <= i; ++j) {
      sum += signal[j];
      count++;
    }
    filtered.push(sum / count);
  }
  // Normalize
  const maxAbs = Math.max(...filtered.map(Math.abs)) || 1;
  return filtered.map(v => v / maxAbs);
}

// Connect to signaling server
const socket = io(SIGNALING_SERVER);

socket.on('connect', () => {
  console.log('Connected to signaling server as', socket.id);
});

socket.on('signal', async ({ from, message }) => {
  if (!peerConnection) {
    await createPeerConnection(from);
  }
  if (message.sdp) {
    await peerConnection.setRemoteDescription(new wrtc.RTCSessionDescription(message.sdp));
    if (message.sdp.type === 'offer') {
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);
      socket.emit('signal', { target: from, message: { sdp: peerConnection.localDescription } });
    }
  } else if (message.candidate) {
    await peerConnection.addIceCandidate(new wrtc.RTCIceCandidate(message.candidate));
  }
});

socket.on('receiver-ready', async ({ receiverId }) => {
  console.log('Receiver ready:', receiverId);
  // Clean up old connection if any
  if (peerConnection) {
    try { peerConnection.close(); } catch (e) {}
    peerConnection = null;
  }
  if (audioTimer) { clearInterval(audioTimer); audioTimer = null; }
  if (audioBufferInterval) { clearInterval(audioBufferInterval); audioBufferInterval = null; }
  if (heatmapInterval) { clearInterval(heatmapInterval); heatmapInterval = null; }
  // Start new connection
  await createPeerConnection(receiverId);
});

async function createPeerConnection(target) {
  peerConnection = new wrtc.RTCPeerConnection({
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      {
        urls: 'turn:openrelay.metered.ca:80',
        username: 'openrelayproject',
        credential: 'openrelayproject'
      }
    ]
  });

  // Create audio track
  const { RTCAudioSource } = wrtc.nonstandard;
  audioSource = new RTCAudioSource();
  const track = audioSource.createTrack();
  peerConnection.addTrack(track);

  // --- HEATMAP DATA CHANNEL ---
  heatmapChannel = peerConnection.createDataChannel('heatmap');
  heatmapChannel.onopen = () => {
    console.log('Heatmap data channel open');
    // Start sending heatmap periodically
    heatmapInterval = setInterval(async () => {
      try {
        const res = await axios.get(`${DAQ_SERVER}/heatmap`);
        if (res.data && res.data.heatmap) {
          heatmapChannel.send(JSON.stringify(res.data));
        }
      } catch (err) {
        // Optionally log error
      }
    }, 200);
  };
  heatmapChannel.onclose = () => {
    console.log('Heatmap data channel closed');
    if (heatmapInterval) clearInterval(heatmapInterval);
  };
  // --- END HEATMAP DATA CHANNEL ---

  // Listen for pixel selection/mode from frontend
  heatmapChannel.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'pixel') {
        selectedPixel = { x: msg.x, y: msg.y };
        audioMode = msg.mode;
        console.log('Selected pixel:', selectedPixel, 'Mode:', audioMode);
        // Restart audio streaming with new selection
        if (audioTimer) clearInterval(audioTimer);
        startAudioStreaming();
      }
    } catch (err) {}
  };

  peerConnection.onicecandidate = ({ candidate }) => {
    if (candidate) {
      socket.emit('signal', { target, message: { candidate } });
    }
  };

  // Initiate offer if we are the sender
  const offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  socket.emit('signal', { target, message: { sdp: peerConnection.localDescription } });

  peerConnection.onconnectionstatechange = () => {
    console.log('Connection state:', peerConnection.connectionState);
    if (peerConnection.connectionState === 'disconnected' || peerConnection.connectionState === 'closed') {
      if (heatmapInterval) clearInterval(heatmapInterval);
      if (audioTimer) clearInterval(audioTimer);
    }
  };

  // Start with no audio until pixel is selected
};

async function startAudioStreaming() {
  if (!selectedPixel) return;
  // Fetch audio data from DAQ server
  audioTimer = setInterval(async () => {
    try {
      const res = await axios.get(`${DAQ_SERVER}/audio_data`);
      if (!res.data || !res.data.audio_data) return;
      const audioData = res.data.audio_data; // [channels][samples] or [samples][channels]
      // Ensure shape: [samples][channels]
      let samples = audioData;
      if (Array.isArray(audioData[0]) && audioData[0].length !== undefined && audioData.length < audioData[0].length) {
        // Transpose if needed
        samples = audioData[0].map((_, c) => audioData.map(r => r[c]));
      }
      // Get audio for selected pixel
      let output;
      if (audioMode === 'processed') {
        // Spatial filter
        const filtered = spatialFilter(samples, selectedPixel.x, selectedPixel.y);
        // Low-pass filter
        output = lowPassFilter(filtered, 44100);
      } else {
        // Raw: just pick one channel (e.g., channel 0)
        output = samples.map(row => row[0]);
      }
      // Convert to Int16Array for PCM
      const pcm = Int16Array.from(output.map(v => Math.max(-1, Math.min(1, v)) * 32767));
      audioSource.onData({
        samples: pcm,
        sampleRate: 44100,
        bitsPerSample: 16,
        channelCount: 1,
        numberOfFrames: pcm.length
      });
    } catch (err) {}
  }, 10); // 10ms chunks
} 