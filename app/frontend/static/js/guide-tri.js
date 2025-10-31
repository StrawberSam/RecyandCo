let consigneData = null;

function chargerConsignes() {
  fetch('/api/rules')
  .then(response => response.json())
  .then(data => {
    consigneData = data;
    rendreSearchCliquable();
  })
  .catch(error => {
    log.error('Erreur de chargement: ', error)
  })
}

function rendreSearchCliquable() {
  const bouton = document.getElementById('search-button');

  bouton.addEventListener('click', () =>{
    rechercherDechets();
  });
}

function rechercherDechets() {
  // Récupérer l'input et la valeur
  const recherche = document.getElementById('search-input').value;

  let resultats = [];

  for (let couleur in consigneData) {
    // parcours chaque dechet de cette couleur
    const dechetsDeLaCouleur = consigneData[couleur];
    // filtrer ceux qui correspondent à la recherche
    const dechetsTrouves = dechetsDeLaCouleur.filter(function(dechet) {
      return dechet.mots_cles.includes(recherche);
    });
    resultats.push(...dechetsTrouves);
  }
  afficherResultat(resultats);
}

function afficherResultat(resultats) {
  const container = document.getElementById('result-container');

  container.innerHTML = '';

  if (resultats.length === 0) {
    container.innerHTML = '<p>Aucun résultat trouvé</p>'
    return;
  }

  // pour chaque déchet, créer une carte
  resultats.forEach(dechet => {
    // carte principale
    const cartePrincipale = document.createElement('div');
    cartePrincipale.className = 'result-card';

    //img
    const icon = document.createElement('img');
    icon.src = `/static/icons/` + dechet.icon;
    icon.alt = dechet.nom;
    icon.className = 'dechet-icon';
    cartePrincipale.appendChild(icon);

    //titre
    const title = document.createElement('h2');
    title.textContent = `${dechet.nom}`;
    cartePrincipale.appendChild(title);

    //poubelle
    const poubelle = document.createElement('p');
    poubelle.className = 'poubelle';
    poubelle.textContent = `Poubelle ${dechet.poubelle}`;
    cartePrincipale.appendChild(poubelle);

    //description
    const desc = document.createElement('p');
    desc.className = 'description';
    desc.textContent = `${dechet.description}`;
    cartePrincipale.appendChild(desc);

    //bon à savoir
    const bonASavoir = document.createElement('p');
    bonASavoir.className = 'bon-a-savoir';

    const strong = document.createElement('strong');
    strong.textContent = 'Bon à savoir : ';
    bonASavoir.appendChild(strong);

    bonASavoir.appendChild(document.createTextNode(dechet.bon_a_savoir));

    cartePrincipale.appendChild(bonASavoir);
    container.appendChild(cartePrincipale);
  });
}

document.addEventListener('DOMContentLoaded', chargerConsignes);
