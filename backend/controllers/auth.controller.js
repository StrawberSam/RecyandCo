// Controller auth : gère la logique des requêtes HTTP pour l'authentification

const authRegister = (req, res) => {
  res.send('register user');
}

const authLogin = (req, res) => {
  res.send('login user');
}

export {authRegister, authLogin};
