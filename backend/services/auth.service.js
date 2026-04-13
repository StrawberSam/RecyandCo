import { PrismaClient } from '../generated/prisma/index.js';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { validateRegisterData } from '../utils/validation.utils.js';
const prisma = new PrismaClient();

// Service auth : gère la logique métier de l'authentification (inscription, connexion)

async function register(username, email, password) {
  validateRegisterData(username, email, password) // Vérifications dans fichier utils

  // Vérification unicité db
  const user = await prisma.user.findUnique({ where: { username: username } });
  const mail = await prisma.user.findUnique({ where: { email: email } });

  if (user) {
    throw new Error('Nom d\'utilisateur déjà utilisé');
  }
  if (mail) {
    throw new Error('Email déjà utilisé');
  }

  const password_hash = await bcrypt.hash(password, 10);

  // Sauvegarde DB
  const newUser = await prisma.user.create({data: {
    username: username,
    email: email,
    password_hash: password_hash
  }
  })

  return {
    "success": true,
    "data": {
      id: newUser.id,
      username: newUser.username,
      email: newUser.email,
      created_at: newUser.created_at
    },
  }
}

async function login(email, password) {
  // Authentifie un utilisateur et génère des tokens JWT.

  if (email == '' || password == '') {
    throw new Error('Email ou mot de passe manquant')
  }

  const user = await prisma.user.findUnique({ where: { email: email } });
  if (!user) {
    throw new Error('Email introuvable')
  }

  const isPasswordValid = await bcrypt.compare(password, user.password_hash);
  if (!isPasswordValid) {
    throw new Error('Mot de passe incorrect')
  }

  // Génération Tokens
  const access_token = jwt.sign(
  { id: user.id, username: user.username },
  process.env.JWT_SECRET,
  { expiresIn: process.env.JWT_EXP }
  )

  const refresh_token = jwt.sign(
  { id: user.id },
  process.env.JWT_SECRET,
  { expiresIn: process.env.JWT_REFRESH_EXP }
  )

  await prisma.user.update({
  where: { id: user.id },
  data: { last_login_at: new Date() }
})

  return {
    "success": true,
    "data": {
      "access_token": access_token,
      "refresh_token": refresh_token,
      "user": {
        "id": user.id,
        "username": user.username
      }
    }
  }
}

export {register, login};
