import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import { validateRegisterData } from '../utils/validation.utils';
const prisma = new PrismaClient();

// Service user : gère la logique métier des opérations CRUD pour les utilisateurs

async function userGet(id) {
  const user = await prisma.user.findUnique({ where: { id: id } });
  if (!user) {
    const err = new Error('Utilisateur introuvable');
    err.status = 404;
    throw err;
  }
  return {
    "success": true,
    "data": {
      "id": user.id,
      "username": user.username,
      "created_at": user.created_at,
      "last_login_at": user.last_login_at
    }
  }
}

async function userUpdate(id, username, password, email) {

  validateRegisterData(username, email, password);

  const user = await prisma.user.findUnique({ where: { id: id } });
  if (!user) {
    const err = new Error('Utilisateur introuvable');
    err.status = 404;
    throw err;
  }

  const new_password = await bcrypt.hash(password, 10);

  const updatedUser = await prisma.user.update({
    where: { id: user.id },
    data: {
      username: username,
      email: email,
      password_hash: new_password }
  })

  return {
    "success": true,
    "data": {
      "id": user.id,
      "username": updatedUser.username,
      "created_at": user.created_at,
      "last_login_at": user.last_login_at
    }
  }
}

async function userDelete(id) {
  const user = await prisma.user.findUnique({ where: { id: id } });
  if (!user) {
    const err = new Error('Utilisateur introuvable');
    err.status = 404;
    throw err;
  }

  await prisma.user.delete({ where: { id: id } });

  return { "success": true, "message": "Utilisateur supprimé" }
}

export { userGet, userUpdate, userDelete }
