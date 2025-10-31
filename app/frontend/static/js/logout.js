// ============================================
// GESTION DE LA DÉCONNEXION
// ============================================

/**
 * Déconnecte l'utilisateur
 */
async function logout() {
    log.debug('🚪 Déconnexion en cours...');

    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            log.debug('✅ Déconnexion réussie');

            // Mettre à jour l'interface immédiatement
            if (typeof window.updateHeaderAuthState === 'function') {
                window.updateHeaderAuthState(null);
            }

            // Afficher un message de confirmation
            alert('Vous êtes déconnecté. À bientôt ! 👋');

            // Rediriger vers la page d'accueil
            setTimeout(() => {
                window.location.href = '/';
            }, 500);

        } else {
            log.error('❌ Erreur lors de la déconnexion:', data);
            window.location.href = '/';
        }

    } catch (error) {
        log.error('❌ Erreur réseau:', error);
        window.location.href = '/';
    }
}

// ============================================
// INITIALISATION AU CHARGEMENT DU DOM
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    log.debug('🔌 Script logout.js chargé');

    const logoutBtn = document.getElementById('logout-btn');

    if (logoutBtn) {
        log.debug('✅ Bouton de déconnexion trouvé, événement attaché');

        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            log.debug('👆 Clic sur le bouton de déconnexion');
            logout();
        });
    } else {
        log.debug('ℹ️ Bouton de déconnexion non trouvé');
    }
});
