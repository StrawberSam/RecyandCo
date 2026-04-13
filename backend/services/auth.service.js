import { PrismaClient } from '../generated/prisma/index.js';
import bcrypt from 'bcrypt';
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

export {register};
