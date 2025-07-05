// index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => res.send({ status: 'OK' }));

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
