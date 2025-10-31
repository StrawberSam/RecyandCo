async function init() {
  try {
    // Récupération des infos utilisateur
    const userData = await getUserData()

    // Affichage des infos utilisateur
    displayUserInfo(userData)

    // Récupérer les statistiques
    const statsData = await getStats()
    log.debug('🔍 statsData AVANT displayStats:', statsData);

    // Affichage des stats
    displayStats(statsData)

    //Récupération des badges
    const badgesData = await getBadges()

    // Affichage des badges
    displayBadges(badgesData)
  } catch (error) {
    // Si quelque chose ne va pas
    log.error('Erreur lors du chargement du profil: ', error)

    // Reidrection vers la page de connexion

  }
}

async function getUserData() {
  const response = await fetchWithAuth ('/api/me', {
    method: 'GET',
    })

  if (!response.ok) {
    throw new Error('Utilisateur non connecté')
  }

  const json = await response.json()

  if (json.data) {
    return json.data
  }

  return json
}

function displayUserInfo(userData) {
  // Pseudo
  const pseudoElement = document.getElementById('user-pseudo')
  if (pseudoElement) {
    pseudoElement.textContent = userData.username
  }

  // Mail
  const emailElement = document.getElementById('user-email')
  if (emailElement) {
    emailElement.textContent = userData.email
  }

  // Score total
  const scoreElement = document.getElementById('user-score')
  if (scoreElement) {
    scoreElement.textContent = userData.total_score
  }

  // Date inscription
  const createdAtElement = document.getElementById('user-created-at')
  if (createdAtElement) {
    const date = new Date(userData.created_at)
    const formattedDate = date.toLocaleDateString('fr-FR')
    createdAtElement.textContent = formattedDate
  }
}

async function getStats() {
  log.debug('Récupération des stats');
  const response = await fetchWithAuth('/api/stats/me', {
    method: 'GET'
  })

  log.debug('Statut de la réponse : ', response.status);

  if (!response.ok) {
    throw new Error('Impossible de récupérer les statistiques')
  }

  const json = await response.json()
  log.debug('Réponse complète:', json);
  log.debug('json.data:', json.data);

  // Extraire les données
  if (json.data) {
    log.debug('Stats extraites:', json.data);
    return json.data
  }
  log.debug('Stats retournées directement:', json.data)
  return json
}

function displayStats(statsData) {
  log.debug('🎨 Affichage des stats:', statsData);
  document.getElementById('stats-games').textContent = statsData.parties_jouees
  document.getElementById('stats-best').textContent = statsData.points
  document.getElementById('stats-correct').textContent = statsData.correct_items
}

async function getBadges() {
  const response = await fetchWithAuth('/api/badges/me', {
    method: 'GET'
  })

  if (!response.ok) {
    throw new Error('Impossible de récupérer les badges')
  }

  const json = await response.json()

  // Extraire les données
  if (json.data) {
    return json.data
  }

  return json
}

function displayBadges(badgesData) {
  log.debug('🏅 Badges reçus:', badgesData)

  // TODO : Afficher les badges dans le HTML
  // Pour l'instant on log juste pour voir ce qu'on reçoit
}

// Lancement au chargement de la page
document.addEventListener('DOMContentLoaded', init)
