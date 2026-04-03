import express from 'express';
const router = express.Router();

// Opérations CRUD
router.get('/:id', (req, res) => {
  res.send('get user');
});

router.patch('/:id', (req, res) => {
  res.send('modifie user');
});

router.delete('/:id', (req, res) => {
  res.send('delete user');
});

export default router;
