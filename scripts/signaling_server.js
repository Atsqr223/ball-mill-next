// Node.js WebRTC Signaling Server using socket.io
const http = require('http');
const socketIo = require('socket.io');

const PORT = 65505;

const server = http.createServer();
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('signal', (data) => {
    // Relay signaling data to the target peer
    const { target, message } = data;
    if (target) {
      io.to(target).emit('signal', { from: socket.id, message });
      console.log(`Relayed signal from ${socket.id} to ${target}`);
    }
  });

  socket.on('ready', () => {
    // Broadcast to all other clients (the sender)
    socket.broadcast.emit('receiver-ready', { receiverId: socket.id });
    console.log(`Receiver ready: ${socket.id}`);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });

  // Let the client know their socket id
  socket.emit('your-id', socket.id);
});

server.listen(PORT, () => {
  console.log(`Signaling server running on port ${PORT}`);
}); 