// ============================================
// GESTION DU REFRESH TOKEN
// ============================================

/**
 * Rafraîchit l'access_token quand il expire
 */
async function refreshAccessToken() {
    log.debug('🔄 Tentative de rafraîchissement du token...');

    try {
        const response = await fetch('/api/refresh', {
            method: 'POST',
            credentials: 'include' // ← Envoie automatiquement le cookie refresh_token
        });

        const data = await response.json();

        if (response.ok && data.success === true) {
            // ✅ Nouveau access_token reçu
            log.debug('✅ Nouveau access_token obtenu !');
            return true;
        } else {
            // ❌ Refresh_token invalide ou expiré → reconnexion nécessaire
            log.error('❌ Refresh token invalide:', data.message);
            window.location.href = '/auth';
            return false;
        }
    } catch (error) {
        log.error('❌ Erreur lors du refresh:', error);
        window.location.href = '/auth';
        return false;
    }
}

/**
 * Fonction helper pour faire des requêtes API avec gestion automatique du refresh
 */
async function fetchWithAuth(url, options = {}) {
    const config = {
        ...options,
        credentials: 'include',
        headers: {
            ...options.headers,
            'Content-Type': 'application/json'
        }
    };

    // Première tentative
    let response = await fetch(url, config);

    // Si 401 → Token expiré, on essaie de le rafraîchir
    if (response.status === 401) {
        log.debug('⚠️ Access token expiré (401), tentative de refresh...');

        const refreshSuccess = await refreshAccessToken();

        if (refreshSuccess) {
            log.debug('🔄 Réessai de la requête avec le nouveau token...');
            // Réessaye la requête avec le nouveau token
            response = await fetch(url, config);
            log.debug('✅ Requête terminée, statut:', response.status);
        } else {
            // le refresh a échoué, redirection vers login
            log.error('Impossible de rafraichîr le token')
            throw new Error('Session expirée')

        }
    }

    return response;
}

// ============================================
// GESTION DE L'ÉTAT D'AUTHENTIFICATION
// ============================================

/**
 * Vérifie si l'utilisateur est connecté en appelant /api/me
 * @returns {Promise<Object|null>} Les données utilisateur ou null
 */
async function checkAuthStatus() {
    try {
        // NE PAS utiliser fetchWithAuth() ici pour éviter les boucles infinies
        // On veut juste vérifier l'état, pas forcer un refresh
        const response = await fetch('/api/me', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();

            if (data.success && data.data) {
                log.debug('✅ Utilisateur connecté:', data.data.username);
                return data.data;  // { id, username, email, total_score }
            }
        }

        // Si 401 ou toute autre erreur, on considère l'utilisateur déconnecté
        log.debug('❌ Utilisateur non connecté');
        return null;

    } catch (error) {
        log.error('❌ Erreur lors de la vérification:', error);
        return null;
    }
}

/**
 * Met à jour UNIQUEMENT les boutons Connexion/Déconnexion dans le header
 * @param {Object|null} userData - Les données utilisateur ou null
 */
function updateHeaderAuthState(userData) {
    // Récupérer les éléments du header
    const loginLink = document.getElementById('auth-link-login');
    const logoutBtn = document.getElementById('logout-btn');

    if (!loginLink || !logoutBtn) {
        log.error('❌ Éléments d\'authentification introuvables dans le header');
        return;
    }

    if (userData) {
        // ========================================
        // UTILISATEUR CONNECTÉ
        // ========================================
        log.debug('🔄 Mise à jour header : utilisateur connecté');

        // Cacher le lien "Connexion"
        loginLink.style.display = 'none';

        // Afficher le bouton "Déconnexion"
        logoutBtn.style.display = 'inline-block';

    } else {
        // ========================================
        // UTILISATEUR DÉCONNECTÉ
        // ========================================
        log.debug('🔄 Mise à jour header : utilisateur déconnecté');

        // Afficher le lien "Connexion"
        loginLink.style.display = 'inline-block';

        // Cacher le bouton "Déconnexion"
        logoutBtn.style.display = 'none';
    }
}

/**
 * Initialise l'état d'authentification au chargement de la page
 */
async function initAuthState() {
    log.debug('🔄 Initialisation de l\'état d\'authentification...');

    const userData = await checkAuthStatus();
    updateHeaderAuthState(userData);

    // Retourner les données pour que d'autres scripts puissent les utiliser
    return userData;
}

// ============================================
// AUTO-INITIALISATION AU CHARGEMENT DU DOM
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthState);
} else {
    // Le DOM est déjà chargé
    initAuthState();
}

// ============================================
// EXPORT POUR UTILISATION DANS D'AUTRES SCRIPTS
// ============================================

// Rendre toutes les fonctions disponibles globalement
window.refreshAccessToken = refreshAccessToken;
window.fetchWithAuth = fetchWithAuth;
window.checkAuthStatus = checkAuthStatus;
window.updateHeaderAuthState = updateHeaderAuthState;
window.initAuthState = initAuthState;
