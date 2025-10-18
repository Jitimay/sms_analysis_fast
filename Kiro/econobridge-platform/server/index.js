import express from 'express';
import cors from 'cors';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const PORT = 3001;
const JWT_SECRET = 'econobridge-secret';

app.use(cors());
app.use(express.json());

// In-memory storage (replace with database in production)
let users = [];
let transactions = [];

// Credit scoring AI function
const calculateCreditScore = (user) => {
  const userTxs = transactions.filter(tx => tx.from === user.walletId || tx.to === user.walletId);
  const totalTxs = userTxs.length;
  const daysSinceRegistration = Math.floor((Date.now() - new Date(user.createdAt)) / (1000 * 60 * 60 * 24));
  const avgTxAmount = userTxs.reduce((sum, tx) => sum + tx.amount, 0) / (totalTxs || 1);
  
  // Simple ML-like scoring algorithm
  let score = 50; // Base score
  score += Math.min(totalTxs * 2, 30); // Transaction frequency
  score += Math.min(daysSinceRegistration * 0.5, 15); // Account age
  score += Math.min(avgTxAmount * 0.01, 5); // Transaction size
  
  return Math.min(Math.max(score, 0), 100);
};

// Auth middleware
const authenticateToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Access denied' });
  
  try {
    const verified = jwt.verify(token, JWT_SECRET);
    req.user = verified;
    next();
  } catch (error) {
    res.status(400).json({ error: 'Invalid token' });
  }
};

// Routes
app.post('/api/register', async (req, res) => {
  const { name, email, phone, password, location } = req.body;
  
  if (users.find(u => u.email === email)) {
    return res.status(400).json({ error: 'User already exists' });
  }
  
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = {
    id: uuidv4(),
    walletId: `WALLET_${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
    name,
    email,
    phone,
    location,
    password: hashedPassword,
    balance: 1000, // Starting balance
    createdAt: new Date().toISOString()
  };
  
  users.push(user);
  const token = jwt.sign({ id: user.id }, JWT_SECRET);
  
  res.json({ token, user: { ...user, password: undefined } });
});

app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const user = users.find(u => u.email === email);
  
  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(400).json({ error: 'Invalid credentials' });
  }
  
  const token = jwt.sign({ id: user.id }, JWT_SECRET);
  res.json({ token, user: { ...user, password: undefined } });
});

app.get('/api/profile', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  
  const creditScore = calculateCreditScore(user);
  res.json({ ...user, password: undefined, creditScore });
});

app.post('/api/send', authenticateToken, (req, res) => {
  const { toWalletId, amount } = req.body;
  const sender = users.find(u => u.id === req.user.id);
  const receiver = users.find(u => u.walletId === toWalletId);
  
  if (!receiver) return res.status(404).json({ error: 'Receiver not found' });
  if (sender.balance < amount) return res.status(400).json({ error: 'Insufficient balance' });
  
  const fee = amount * 0.01; // 1% fee
  const netAmount = amount - fee;
  
  sender.balance -= amount;
  receiver.balance += netAmount;
  
  const transaction = {
    id: uuidv4(),
    from: sender.walletId,
    to: toWalletId,
    amount: netAmount,
    fee,
    timestamp: new Date().toISOString()
  };
  
  transactions.push(transaction);
  res.json({ transaction, newBalance: sender.balance });
});

app.get('/api/transactions', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.id);
  const userTxs = transactions.filter(tx => tx.from === user.walletId || tx.to === user.walletId);
  res.json(userTxs);
});

app.get('/api/admin/dashboard', (req, res) => {
  const totalUsers = users.length;
  const totalTransactions = transactions.length;
  const avgCreditScore = users.reduce((sum, user) => sum + calculateCreditScore(user), 0) / totalUsers || 0;
  const totalVolume = transactions.reduce((sum, tx) => sum + tx.amount, 0);
  
  res.json({
    totalUsers,
    totalTransactions,
    avgCreditScore: Math.round(avgCreditScore),
    totalVolume,
    users: users.map(u => ({ ...u, password: undefined, creditScore: calculateCreditScore(u) })),
    recentTransactions: transactions.slice(-10)
  });
});

app.post('/api/sms', (req, res) => {
  const { message } = req.body;
  const match = message.match(/SEND (\d+) to (\w+)/i);
  
  if (!match) return res.status(400).json({ error: 'Invalid SMS format' });
  
  const [, amount, toWalletId] = match;
  res.json({ message: `Processing transfer of ${amount} to ${toWalletId}` });
});

app.listen(PORT, () => {
  console.log(`EconoBridge server running on port ${PORT}`);
});
