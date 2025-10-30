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
    credentials: 'include', // envoie et reçoit les cookies
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

        // Rediriger vers le jeu
        showMessage('Connexion réussie! Redirection...', 'success');

        setTimeout(function () {
          window.location.href = '/';
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
function handleRegister() {
  console.log('tentative d\'inscription');

  // Récupération des valeurs du formulaire
  let email = document.getElementById('register-email').value;
  let password = document.getElementById('register-password').value;
  let username = document.getElementById('register-username').value;

  // Masquer anciens messages
  hideMessage();

  // Envoyer la requête à l'API
  fetch('/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify({
      username: username,
      email: email,
      password: password
    })
  })
    .then(response => response.json())
    .then(data => {
      console.log('réponse reçue :', data);

      if (data.success === true) {
        console.log('Inscription réussie');

        // Rediriger vers la connexion après inscription réussie
        showMessage('Inscription réussie! Redirection...', 'success');

        setTimeout(function () {
          window.location.href = '/auth';
        }, 1000);

      } else {
        // Identifiant incorrect
        console.log('Inscription échouée');
        showMessage(data.message, 'error');
      }
    })
    .catch(error => {
      console.error('erreur réseau:', error);
      showMessage('Erreur de connexion. Vérifier votre connexion internet.', 'error');
    });
}

// Affiche/cacher le mot de passe
// =============================
function togglePasswordVisibility(inputId, iconElement) {
  let passwordInput = document.getElementById(inputId);

  if (passwordInput.type === 'password') {
    // Montrer le mot de passe
    passwordInput.type = 'text';
    iconElement.textContent = '🙈'; // Change l'icône
  } else {
    // Cacher le mot de passe
    passwordInput.type = 'password';
    iconElement.textContent = '👁️'; // Remet l'icône initiale
  }
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

  // === Réinitialisation complète des formulaires ===

  // 1. Vider tous les champs
  document.getElementById('email').value = '';
  document.getElementById('password').value = '';
  document.getElementById('register-username').value = '';
  document.getElementById('register-email').value = '';
  document.getElementById('register-password').value = '';

  // 2. Remettre les inputs en type password
  document.getElementById('password').type = 'password';
  document.getElementById('register-password').type = 'password';

  // 3. Remettre toutes les icônes en 👁️
  let allIcons = document.querySelectorAll('.toggle-password');
  allIcons.forEach(function(icon) {
    icon.textContent = '👁️';
  });

  // 4. Masquer les messages d'erreur
  hideMessage();
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
