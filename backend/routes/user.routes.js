import express from 'express';
import { deleteUser, getUser, updateUser } from '../controllers/user.controller.js';
const router = express.Router();

// Opérations CRUD
router.get('/:id', getUser);

router.patch('/:id', updateUser);

router.delete('/:id', deleteUser);

export default router;
