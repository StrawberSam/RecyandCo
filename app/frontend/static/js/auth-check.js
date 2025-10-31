// ============================================
// Vérifie si l'utilisateur a un JWT valide
// ============================================

// Vérification si l'utilisateur est connecté
async function estConnecte() {
  try {
    const res = await fetchWithAuth('/api/me', { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

// Récupère les infos de l'utilisateur depuis l'API
async function getInfosUtilisateur() {
  if (!estConnecte()) {
    return null;
  }

  try {
    const response = await fetchWithAuth('/api/me', {
      method: 'GET'
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();

    if (data.success && data.data) {
      return {
        username: data.data.username || 'Utilisateur',
        total_score: data.data.total_score || 0
      };
    }

    return null;
  } catch (error) {
    log.error('Erreur lors de la récupération des infos utilisateur:', error);
    return null;
  }
}

// Redirection vers la page de connexion avec un message
function redirigerVersConnexion(message) {
  if (message) {
    sessionStorage.setItem('auth_message', message);
  }
  window.location.href = '/auth';
}

// Protéger une page si non connecté : rediriger
async function protegerPage() {
  const connecte = await estConnecte();
  if (!connecte) {
    redirigerVersConnexion('Vous devez vous connecter pour accéder à cette page.');
  }
}
