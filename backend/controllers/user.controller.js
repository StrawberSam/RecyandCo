// Controller user : gère la logique des requêtes HTTP pour les utilisateurs

import { userDelete, userGet, userUpdate } from "../services/user.service.js";

async function getUser(req, res) {
  try {
    // Récupération des données
    const { id } = req.params;

    // Appeler le service
    const result = await userGet(id);

    // Retourne la réponse
    res.status(200).json(result);
  } catch (error) {
    // Gère les erreurs
    res.status(error.status || 400).json({success: false, message: error.message});
  }
}

async function updateUser(req, res) {
  try {
    // Récupération des données
    const { username, email, password } = req.body;
    const { id } = req.params;

    // Appeler le service
    const result = await userUpdate(id, username, email, password);

    // Retourne la réponse
    res.status(200).json(result);
  } catch (error) {
    // Gère les erreurs
    res.status(error.status || 400).json({success: false, message: error.message});
  }
}

async function deleteUser(req, res) {
  try {
    // Récupération des données
    const { id } = req.params;

    // Appeler le service
    const result = await userDelete(id);

    // Retourne la réponse
    res.status(200).json(result);
  } catch (error) {
    // Gère les erreurs
    res.status(error.status || 400).json({success: false, message: error.message});
  }
}

export {getUser, updateUser, deleteUser};
