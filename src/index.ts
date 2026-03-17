import express, { Request, Response, NextFunction } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import cors from 'cors';

const app = express();
const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'secret';

app.use(cors());
app.use(express.json());

// Extend Express Request to include user
declare global {
  namespace Express {
    interface Request {
      user?: any;
    }
  }
}

// Middleware: Require Auth
const requireAuth = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'No token provided' });
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// ======================= AUTH =======================

app.post('/api/auth/register', async (req: Request, res: Response) => {
  const { nombre, email, password, is_runner } = req.body;
  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({
      data: { nombre, email, password: hashedPassword, is_runner: !!is_runner },
    });
    res.status(201).json({ message: 'User created', userId: user.id });
  } catch (error: any) {
    res.status(400).json({ error: 'Error creating user', details: error.message });
  }
});

app.post('/api/auth/login', async (req: Request, res: Response) => {
  const { email, password } = req.body;
  try {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(401).json({ error: 'Invalid credentials' });
    const token = jwt.sign({ userId: user.id, is_runner: user.is_runner }, JWT_SECRET, { expiresIn: '1d' });
    res.json({ token, user: { id: user.id, nombre: user.nombre, email: user.email, is_runner: user.is_runner } });
  } catch (error: any) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ======================= TASKS =======================

app.get('/api/tasks', requireAuth, async (req: Request, res: Response) => {
  try {
    const tasks = await prisma.task.findMany({ include: { creator: true, runner: true } });
    res.json(tasks);
  } catch (error: any) {
    res.status(500).json({ error: 'Error fetching tasks' });
  }
});

app.post('/api/tasks', requireAuth, async (req: Request, res: Response) => {
  const { titulo, descripcion, categoria, precio_inicial, lat, lng } = req.body;
  try {
    const task = await prisma.task.create({
      data: {
        titulo,
        descripcion,
        categoria,
        precio_inicial,
        lat,
        lng,
        creator_id: req.user.userId,
      },
    });
    res.status(201).json(task);
  } catch (error: any) {
    res.status(400).json({ error: 'Error creating task', details: error.message });
  }
});

// ======================= OFFERS =======================

app.post('/api/offers', requireAuth, async (req: Request, res: Response) => {
  const { task_id, precio_propuesto, mensaje } = req.body;
  try {
    // Validation: Check if task exists and is OPEN
    const task = await prisma.task.findUnique({ where: { id: task_id } });
    if (!task) return res.status(404).json({ error: 'Task not found' });
    if (task.estado !== 'OPEN') return res.status(400).json({ error: 'Task is not OPEN' });

    // Validation: Self-offer restriction
    if (task.creator_id === req.user.userId) {
      return res.status(400).json({ error: 'Cannot bid on your own task' });
    }

    const offer = await prisma.offer.create({
      data: {
        task_id,
        runner_id: req.user.userId,
        precio_propuesto,
        mensaje,
      },
    });
    res.status(201).json(offer);
  } catch (error: any) {
    res.status(400).json({ error: 'Error creating offer', details: error.message });
  }
});

app.patch('/api/offers/:id/accept', requireAuth, async (req: Request, res: Response) => {
  const offerId = parseInt(req.params.id);
  try {
    const offer = await prisma.offer.findUnique({ where: { id: offerId }, include: { task: true } });
    if (!offer) return res.status(404).json({ error: 'Offer not found' });

    // Validation: Only creator can accept
    if (offer.task.creator_id !== req.user.userId) {
      return res.status(403).json({ error: 'Only the task creator can accept an offer' });
    }

    if (offer.task.estado !== 'OPEN') {
      return res.status(400).json({ error: 'Task is not completely OPEN' });
    }

    // Transaction: Accept offer, update task, reject other offers
    const result = await prisma.$transaction([
      prisma.offer.update({ where: { id: offerId }, data: { estado: 'ACCEPTED' } }),
      prisma.offer.updateMany({
        where: { task_id: offer.task_id, id: { not: offerId } },
        data: { estado: 'REJECTED' },
      }),
      prisma.task.update({
        where: { id: offer.task_id },
        data: {
          estado: 'ASSIGNED',
          runner_id: offer.runner_id,
          precio_final: offer.precio_propuesto,
        },
      }),
    ]);
    res.json({ message: 'Offer accepted successfully', task: result[2] });
  } catch (error: any) {
    res.status(500).json({ error: 'Error accepting offer', details: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
