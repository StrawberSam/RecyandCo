// ============================================
// Vérifie si l'utilisateur a un JWT valide
// ============================================

// Vérification si l'utilisateur est connecté
function estConnecte() {
  let token = localStorage.getItem('access_token');
  return token !== null && token !== undefined && token !== '';
}

// Récupère les infos de l'utilisateur depuis le localStorage
function getInfosUtilisateur() {
  if (!estConnecte()) {
    return null;
  }

  return {
    username: localStorage.getItem('username') || 'Utilisateur',
    total_score: parseInt(localStorage.getItem('total_score')) || 0
  };
}

// Redirection vers la page de connexion avec un message
function redirigerVersConnexion (message) {
  if (message) {
    // stockage du message pour l'afficher sur la page auth
    localStorage.setItem('auth_message', message);
  }
  windows.location.href = '/auth';
}

// Protéger une page si non connecté : rediriger
function protegerPage() {
  if (!estConnecte) {
    redirigerVersConnexion('Vous devez vous connecter pour accéder à cette page.');
  }
}
