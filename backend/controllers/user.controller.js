// Controller user : gère la logique des requêtes HTTP pour les utilisateurs

const getUser = (req, res) => {
  res.send('get user');
}

const updateUser = (req, res) => {
  res.send('update user');
}

const deleteUser = (req, res) => {
  res.send('delete user');
}

export {getUser, updateUser, deleteUser};
