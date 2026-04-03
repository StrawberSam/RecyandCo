import express from 'express';
import { authLogin, authRegister } from '../controllers/auth.controller.js';
const router = express.Router();

// Opération CRUD
router.post('/register', authRegister);

router.post('/login', authLogin);

export default router;
