// variable globale
let consignesData = null;

function chargerConsignes() {
    console.log('📂 Chargement des consignes...');

    fetch('/api/rules')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Fichier chargé !', data);
            consignesData = data;
            rendrepoubelleCliquable();
        })
        .catch(error => {
            console.error('❌ Erreur de chargement :', error);
        });
}

// Rendre les poubelles cliquables
function rendrepoubelleCliquable() {
  // récupérer les poubelles dans le html
  const poubelles = document.querySelectorAll('.poubelle');

  poubelles.forEach(poubelle => {
    poubelle.addEventListener('click', () => {
      const couleur = poubelle.dataset.bin;

      afficherDetailsPoubelle(couleur);
    });
  });
}

function afficherDetailsPoubelle(couleur) {
  // Récupérer le conteneur
  const container = document.getElementById('bins-details');

  // vider le conteneur
  container.innerHTML = '';

  const dechets = consignesData[couleur];

  // création du titre
  const titre = document.createElement('h2');
  titre.textContent = `Poubelle ${couleur}`;
  container.appendChild(titre);

  // créer une liste
  const liste = document.createElement('ul');

  // Parcourir chaque déchet
  dechets.forEach(dechet => {
    const item = document.createElement('li');

    const icon = document.createElement('img');
    icon.src = `/static/icons/` + dechet.icon;
    icon.alt = dechet.nom;
    icon.className = 'dechet-icon';
    item.appendChild(icon);

    const nom = document.createElement('strong');
    nom.textContent = dechet.nom;
    liste.appendChild(nom);

    const bonASavoir = document.createElement('p');
    bonASavoir.className = 'bon-a-savoir';
    bonASavoir.innerHTML = `💡 ${dechet.bon_a_savoir}`;
    item.appendChild(bonASavoir);

    liste.appendChild(item);
  });

  // ajout de la liste au conteneur
  container.appendChild(liste);

}

document.addEventListener('DOMContentLoaded', chargerConsignes);
