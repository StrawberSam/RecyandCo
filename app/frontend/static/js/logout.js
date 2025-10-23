// ============================================
// GESTION DE LA DÉCONNEXION
// ============================================

/**
 * Déconnecte l'utilisateur
 */
async function logout() {
    console.log('🚪 Déconnexion en cours...');

    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            console.log('✅ Déconnexion réussie');

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
            console.error('❌ Erreur lors de la déconnexion:', data);
            window.location.href = '/';
        }

    } catch (error) {
        console.error('❌ Erreur réseau:', error);
        window.location.href = '/';
    }
}

// ============================================
// INITIALISATION AU CHARGEMENT DU DOM
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔌 Script logout.js chargé');

    const logoutBtn = document.getElementById('logout-btn');

    if (logoutBtn) {
        console.log('✅ Bouton de déconnexion trouvé, événement attaché');

        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('👆 Clic sur le bouton de déconnexion');
            logout();
        });
    } else {
        console.log('ℹ️ Bouton de déconnexion non trouvé');
    }
});
