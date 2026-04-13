import validator from 'validator';

function validateRegisterData(username, email, password) {
  if (username == "" || username.length < 3 || username.length > 50) {
    const err = new Error("Nom d'utilisateur invalide");
    err.status = 400;
    throw err;
  }
  if (!validator.isEmail(email)) {
    const err = new Error("Email invalide");
    err.status = 400;
    throw err;
  }
  if (password.length < 8) {
    const err = new Error("Mot de passe trop court. Minimum 8 caractères");
    err.status = 400;
    throw err;
  }
}

export {validateRegisterData};
