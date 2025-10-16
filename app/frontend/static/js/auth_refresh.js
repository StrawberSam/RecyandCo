// ============================================
// GESTION DU REFRESH TOKEN
// ============================================

/**
 * Rafraîchit l'access_token quand il expire
 * Le refresh_token est automatiquement envoyé via le cookie
 */
async function refreshAccessToken() {
    console.log('🔄 Tentative de rafraîchissement du token...');

    try {
        const response = await fetch('/api/refresh', {
            method: 'POST',
            credentials: 'include' // ← Envoie automatiquement le cookie refresh_token
        });

        const data = await response.json();

        if (data.success === true) {
            // ✅ Nouveau access_token reçu
            localStorage.setItem('access_token', data.data.access_token);
            console.log('✅ Nouveau access_token obtenu !');
            return true;
        } else {
            // ❌ Refresh_token invalide ou expiré → reconnexion nécessaire
            console.error('❌ Refresh token invalide:', data.message);
            localStorage.clear();
            window.location.href = '/auth';
            return false;
        }
    } catch (error) {
        console.error('❌ Erreur lors du refresh:', error);
        localStorage.clear();
        window.location.href = '/auth';
        return false;
    }
}

/**
 * Fonction helper pour faire des requêtes API avec gestion automatique du refresh
 */
async function fetchWithAuth(url, options = {}) {
    // Ajoute l'access_token dans le header
    const token = localStorage.getItem('access_token');

    const config = {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': 'Bearer ' + token,
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
            // Réessaye la requête avec le nouveau token
            const newToken = localStorage.getItem('access_token');
            config.headers['Authorization'] = 'Bearer ' + newToken;
            response = await fetch(url, config);
            console.log('✅ Requête réessayée avec le nouveau token');
        }
    }

    return response;
}
