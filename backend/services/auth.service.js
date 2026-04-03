import { PrismaClient } from '../generated/prisma/index.js';
import bcrypt from 'bcrypt';
import validator from 'validator';
const prisma = new PrismaClient();

// Service auth : gère la logique métier de l'authentification (inscription, connexion)

async function register(username, email, password) {
  if (username == "" || username.length < 3 || username.length > 50) {
    throw new Error("Nom d'utilisateur invalide");
  }

  if (!validator.isEmail(email)) {
    throw new Error("Email invalide");
  }

  if (password.length < 8) {
    throw new Error("Mot de passe trop court. Minimum 8 caractères")
  }

  // Vérification unicité db
  const user = await prisma.user.findUnique({ where: { username: username } });
  const mail = await prisma.user.findUnique({ where: { email: email } });

  if (user) {
    throw new Error('Nom d\'utilisateur déjà utilisé');
  }

  if (mail) {
    throw new Error('Email déjà utilisé');
  }

  // Hashage password
  const password_hash = await bcrypt.hash(password, 10);

  // Sauvegarde DB
  const newUser = await prisma.user.create({data: {
    username: username,
    email: email,
    password_hash: password_hash
  }
  })

  // Return
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
