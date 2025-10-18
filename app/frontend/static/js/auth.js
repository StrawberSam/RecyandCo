// AUTHENTIFICATION - LOGIN
// ========================

document.addEventListener('DOMContentLoaded', function() {
  let loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
      event.preventDefault();

      handleLogin();
    });
  }

  // Formulaire d'inscription
    let registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();
            handleRegister();
        });
    }

    // Lien pour basculer entre login/register
    let toggleLink = document.getElementById('toggle-link');
    if (toggleLink) {
        toggleLink.addEventListener('click', function(event) {
            event.preventDefault();
            toggleForms();
        });
    }
});

// Gère la connexion de l'utilisateur
// ==================================

function handleLogin() {
  console.log('tentative de connexion');

  //Récupération des valeurs du formulaire
  let email = document.getElementById('email').value;
  let password = document.getElementById('password').value;

  //masquer anciens messages
  hideMessage();

  // Envoyer la requête à l'API
  fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({
      email: email,
      password: password
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('réponse reçue :', data);

    if (data.success === true) {
      console.log('Connexion réussie');

      // Stocker seulement access_token (refresh dans cookie)
      localStorage.setItem('access_token', data.data.access_token);

      // stocker info utilisateur
      localStorage.setItem('user_id', data.data.user.id);
      localStorage.setItem('username', data.data.user.username);

      // Récupérer score total
      recupererScoreApresLogin();

    } else {
      // identifiant incorrect
      console.log('Connexion échouée');
      showMessage('Email ou mot de passe incorrect', 'error');
    }
  })
  .catch(error => {
    console.error('erreur réseau:', error);
    showMessage('Erreur de connexion. Vérifier votre connexion internet.', 'error');
  });
}

// Gère l'inscription de l'utilisateur
// ==================================
function handleRegister() {
  console.log('Tentative d\'inscription');

  // Récupération des valeurs du formulaire
  let username = document.getElementById('register-username').value;
  let email = document.getElementById('register-email').value;
  let password = document.getElementById('register-password').value;

  // Masquer anciens messages
  hideMessage();

  // ✅ Utilise fetch() normal (pas de token nécessaire pour register)
  fetch('/api/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: username,
        email: email,
        password: password
      })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Réponse reçue :', data);

    if (data.success === true) {
        console.log('Inscription réussie');
        showMessage('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success');

        // Basculer vers le formulaire de login après 2 secondes
        setTimeout(function() {
            toggleForms();
        }, 2000);
    } else {
        console.log('Inscription échouée');
        showMessage(data.message || 'Erreur lors de l\'inscription', 'error');
      }
  })
  .catch(error => {
    console.error('Erreur réseau:', error);
    showMessage('Erreur de connexion. Vérifier votre connexion internet.', 'error');
  });
}

// Bascule entre formulaire login et register
// ==========================================
function toggleForms() {
    let loginForm = document.getElementById('login-form');
    let registerForm = document.getElementById('register-form');
    let toggleText = document.getElementById('toggle-text');
    let toggleLink = document.getElementById('toggle-link');
    let title = document.querySelector('.auth-container h2');

    if (loginForm.style.display === 'none') {
        // Afficher login, cacher register
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        toggleText.textContent = 'Pas encore de compte ?';
        toggleLink.textContent = 'S\'inscrire';
        title.textContent = 'Connexion';
    } else {
        // Afficher register, cacher login
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
        toggleText.textContent = 'Déjà un compte ?';
        toggleLink.textContent = 'Se connecter';
        title.textContent = 'Inscription';
    }
}

function recupererScoreApresLogin() {
  console.log('Récupération du score après connexion');

  let token = localStorage.getItem('access_token');

  fetchWithAuth('/api/scores/me', {
    method: 'GET',
  })
  .then(response => response.json())
  .then(data => {
    console.log('📦 Réponse complète :', data);
    console.log('📊 data.data :', data.data);
    console.log('📊 Est-ce un tableau ?', Array.isArray(data.data));

    // calculer le total des points
    let totalScore = 0;

     if (data.success && data.data && data.data.total_score !== undefined) {
      totalScore = data.data.total_score;
      console.log('💰 Score total récupéré :', totalScore);
    } else {
      console.warn('⚠️ total_score non trouvé, initialisation à 0');
    }

    // stockage du score total
    localStorage.setItem('total_score', totalScore);

    // Rediriger vers le jeu
    showMessage('Connexion réussie! Redirection...', 'success');

    setTimeout(function() {
      window.location.href = '/jeu';
    }, 1000);
  })
  .catch(error => {
    console.error('Erreur lors de la récupération du score:', error);

    // Même si le score échoue, on met 0 et on redirige
    localStorage.setItem('total_score', 0);

    showMessage('Connexion réussie ! Redirection...', 'success');

        setTimeout(function() {
      window.location.href = '/jeu';
    }, 1000);
  })
}

// Affiche message à l'utilisateur
// ===============================
function showMessage(text, type) {
  let messageDiv = document.getElementById('message');

  if (messageDiv) {
    messageDiv.textContent = text;
    messageDiv.className = 'message ' + type;
    messageDiv.style.display = 'block';
  }
}

// masque le message
// =================
function hideMessage() {
  let messageDiv = document.getElementById('message');

  if (messageDiv) {
    messageDiv.style.display = 'none';
  }
}
