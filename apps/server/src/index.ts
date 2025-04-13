import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: 'http://localhost:5173', methods: ['GET', 'POST'] },
});

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('D&D backend running!');
});

// Example socket connection
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  socket.on('roll-dice', (data) => {
    const result = Math.floor(Math.random() * data.sides) + 1;
    io.emit('dice-result', { roller: socket.id, result });
  });

  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });
});

const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
