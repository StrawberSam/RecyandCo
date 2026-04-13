import validator from 'validator';

function validateRegisterData(username, email, password) {
  if (username == "" || username.length < 3 || username.length > 50) {
    throw new Error("Nom d'utilisateur invalide");
  }
  if (!validator.isEmail(email)) {
    throw new Error("Email invalide");
  }
  if (password.length < 8) {
    throw new Error("Mot de passe trop court. Minimum 8 caractères")
  }
}

export {validateRegisterData};
