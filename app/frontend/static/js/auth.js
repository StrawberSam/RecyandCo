// AUTHENTIFICATION - LOGIN
// ========================

document.addEventListener('DOMContentLoaded', function () {
  let loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault();
      handleLogin();
    });
  }

  // Formulaire d'inscription
  let registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', function (event) {
      event.preventDefault();
      handleRegister();
    });
  }

  // Lien pour basculer entre login/register
  let toggleLink = document.getElementById('toggle-link');
  if (toggleLink) {
    toggleLink.addEventListener('click', function (event) {
      event.preventDefault();
      toggleForms();
    });
  }
});

// Gère la connexion de l'utilisateur
// ==================================

function handleLogin() {
  console.log('tentative de connexion');

  // Récupération des valeurs du formulaire
  let email = document.getElementById('email').value;
  let password = document.getElementById('password').value;

  // Masquer anciens messages
  hideMessage();

  // Envoyer la requête à l'API
  fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include', // ✅ Important : envoie et reçoit les cookies
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

        // ✅ Les tokens sont maintenant dans les cookies automatiquement
        // ✅ Plus besoin de localStorage pour les tokens

        // Rediriger vers le jeu
        showMessage('Connexion réussie! Redirection...', 'success');

        setTimeout(function () {
          window.location.href = '/jeu';
        }, 1000);

      } else {
        // Identifiant incorrect
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
function handleLogin() {
  console.log('tentative de connexion');

  // Récupération des valeurs du formulaire
  let email = document.getElementById('email').value;
  let password = document.getElementById('password').value;

  // Masquer anciens messages
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

        // ✅ Rediriger vers le jeu après connexion réussie
        showMessage('Connexion réussie! Redirection...', 'success');

        setTimeout(function () {
          window.location.href = '/jeu';
        }, 1000);

      } else {
        // Identifiant incorrect
        console.log('Connexion échouée');
        showMessage('Email ou mot de passe incorrect', 'error');
      }
    })
    .catch(error => {
      console.error('erreur réseau:', error);
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

// Masque le message
// =================
function hideMessage() {
  let messageDiv = document.getElementById('message');

  if (messageDiv) {
    messageDiv.style.display = 'none';
  }
}
