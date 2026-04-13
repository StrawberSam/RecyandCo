import { login, register } from "../services/auth.service.js";
// Controller auth : gère la logique des requêtes HTTP pour l'authentification

async function authRegister(req, res) {
  try {
    // Récupération des données
    const { username, email, password} = req.body;

    // Appeler le service
    const result = await register(username, email, password);

    // Retourne la réponse
    res.status(201).json(result);
  } catch (error) {
    // Gère les erreurs
    res.status(error.status || 400).json({success: false, message: error.message});
  }
}

async function authLogin(req, res) {
  try {
    // Récupération des données
    const { email, password} = req.body;

    // Appeler le service
    const result = await login(email, password);

    // Retourne la réponse
    res.status(200).json(result);
  } catch (error) {
    // Gère les erreurs
    res.status(error.status || 400).json({success: false, message: error.message});
  }
}

export {authRegister, authLogin};
