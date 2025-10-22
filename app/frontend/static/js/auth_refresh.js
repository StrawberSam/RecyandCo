// ============================================
// GESTION DU REFRESH TOKEN
// ============================================

/**
 * Rafraîchit l'access_token quand il expire
 */
async function refreshAccessToken() {
    console.log('🔄 Tentative de rafraîchissement du token...');

    try {
        const response = await fetch('/api/refresh', {
            method: 'POST',
            credentials: 'include' // ← Envoie automatiquement le cookie refresh_token
        });

        const data = await response.json();

        if (response.ok && data.success === true) {
            // ✅ Nouveau access_token reçu
            console.log('✅ Nouveau access_token obtenu !');
            return true;
        } else {
            // ❌ Refresh_token invalide ou expiré → reconnexion nécessaire
            console.error('❌ Refresh token invalide:', data.message);
            window.location.href = '/auth';
            return false;
        }
    } catch (error) {
        console.error('❌ Erreur lors du refresh:', error);
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
        console.log('⚠️ Access token expiré (401), tentative de refresh...');

        const refreshSuccess = await refreshAccessToken();

        if (refreshSuccess) {
            console.log('🔄 Réessai de la requête avec le nouveau token...');
            // Réessaye la requête avec le nouveau token
            response = await fetch(url, config);
            console.log('✅ Requête terminée, statut:', response.status);
        } else {
            // le refresh a échoué, redirection vers login
            console.error('Impossible de rafraichîr le token')
            throw new Error('Session expirée')

        }
    }

    return response;
}
