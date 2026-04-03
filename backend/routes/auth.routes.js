import express from 'express';
const router = express.Router();

// Opération CRUD
router.post('/register', (req, res) => {
  res.send('create user');
});

router.post('/login', (req, res) => {
  res.send('connect user');
});

export default router;
