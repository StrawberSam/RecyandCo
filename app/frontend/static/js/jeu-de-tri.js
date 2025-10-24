// ============================================
// JEU DE TRI - RÉCY&CO
// ============================================

// 1. Vérification de l'utilisateur si connecté avant de charger le jeu
// ============================================

document.addEventListener('DOMContentLoaded', async function () {
  console.log('🎮 Jeu de tri chargé !');
  tempsDebut = Date.now();
  chargerInfosUtilisateur();
  chargerDechets();

  let btnQuit = document.getElementById('btn-quit');
  if (btnQuit) {
    btnQuit.addEventListener('click', sauvegarderScore);
  }
});

// 2. VARIABLES GLOBALES
// ============================================

// Tous les déchets recyclables (bleue, jaune, verte)
let tousLesDechets = [];

// Carte actuellement sélectionnée (mode clic-clic)
let carteSelectionnee = null;

// score partie en cours
let scoreSession = 0;
// score total du user
let scoreTotalUtilisateur = 0;
// nb total de déchets triés
let nombreTentatives = 0;
// nb de déchet correctement triés
let nombreCorrects = 0;
// timestamp
let tempsDebut = Date.now();

// 3. CHARGEMENT ET FILTRAGE DES DONNÉES
// ============================================

/**
 * Charge le fichier consignes.json depuis le serveur
 */
function chargerDechets() {
    console.log('📂 Chargement du fichier consignes.json...');

    fetch('/api/rules')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Fichier chargé !', data);
            filtrerDechetsJouables(data);
        })
        .catch(error => {
            console.error('❌ Erreur de chargement :', error);
        });
}

/**
 * Filtre pour ne garder que les déchets des 3 poubelles du jeu
 */
function filtrerDechetsJouables(data) {
    console.log('🔍 Filtrage des déchets jouables...');

    let dechetsJouables = [];

    // Ajouter tous les déchets de la poubelle jaune
    if (data.jaune) {
        dechetsJouables = dechetsJouables.concat(data.jaune);
        console.log(`  ➕ ${data.jaune.length} déchets jaunes ajoutés`);
    }

    // Ajouter tous les déchets de la poubelle verte
    if (data.verte) {
        dechetsJouables = dechetsJouables.concat(data.verte);
        console.log(`  ➕ ${data.verte.length} déchets verts ajoutés`);
    }

    // Ajouter tous les déchets de la poubelle bleue
    if (data.bleue) {
        dechetsJouables = dechetsJouables.concat(data.bleue);
        console.log(`  ➕ ${data.bleue.length} déchets bleus ajoutés`);
    }

    // Sauvegarder dans la variable globale
    tousLesDechets = dechetsJouables;

    console.log(`✅ Total : ${tousLesDechets.length} déchets jouables !`);

    // Choisir 7 déchets au hasard et les afficher
    choisir7DechetsAleatoires();
}

/**
 * Mélange un tableau (algorithme Fisher-Yates)
 */
function melangerTableau(tableau) {
    let copie = [...tableau];

    for (let i = copie.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [copie[i], copie[j]] = [copie[j], copie[i]];
    }

    return copie;
}

/**
 * Choisit 7 déchets au hasard parmi tous les déchets jouables
 */
function choisir7DechetsAleatoires() {
    console.log('🎲 Sélection de 7 déchets au hasard...');

    let dechetsmelanges = melangerTableau(tousLesDechets);
    let septDechets = dechetsmelanges.slice(0, 7);

    console.log('✅ 7 déchets sélectionnés');

    afficherCartes(septDechets);
}

// 4. AFFICHAGE DES CARTES
// ============================================

/**
 * Affiche les 7 cartes de déchets dans la zone de jeu
 */
function afficherCartes(lesSeptDechets) {
    console.log('🎨 Création des cartes visuelles...');

    let zoneCartes = document.getElementById('cartes-zone');
    zoneCartes.innerHTML = '';

    lesSeptDechets.forEach(function(dechet, index) {
        console.log(`  📝 Création carte ${index + 1} : ${dechet.nom}`);

        let carte = creerCarte(dechet);
        zoneCartes.appendChild(carte);
    });

    console.log('✅ 7 cartes affichées sur la page !');

    // Initialiser les événements sur les poubelles
    initialiserPoubelles();
}

/**
 * Crée une carte complète pour un déchet
 */
function creerCarte(dechet) {
    let carte = document.createElement('div');
    carte.className = 'carte-dechet';
    carte.dataset.poubelle = dechet.poubelle;
    carte.draggable = true;

    // Ajouter les événements
    ajouterEvenementsDragSurCarte(carte, dechet);
    ajouterEvenementClicSurCarte(carte, dechet);

    // Créer et ajouter l'image et le nom
    let img = creerImageCarte(dechet);
    let nom = creerNomCarte(dechet);

    carte.appendChild(img);
    carte.appendChild(nom);

    return carte;
}

/**
 * Crée l'élément image d'une carte
 */
function creerImageCarte(dechet) {
    let img = document.createElement('img');
    img.src = '/static/icons/' + dechet.icon;
    img.alt = dechet.nom;
    return img;
}

/**
 * Crée l'élément paragraphe (nom) d'une carte
 */
function creerNomCarte(dechet) {
    let nom = document.createElement('p');
    nom.textContent = dechet.nom;
    return nom;
}

// 5. MODE DRAG & DROP (DESKTOP/SOURIS)
// ============================================

/**
 * Ajoute les événements de drag & drop sur une carte
 */
function ajouterEvenementsDragSurCarte(carte, dechet) {
    carte.addEventListener('dragstart', function(event) {
        console.log('🖐️ Début du glissement :', dechet.nom);

        // Stocker les infos dans le dataTransfer
        event.dataTransfer.setData('poubelle-correcte', dechet.poubelle);
        event.dataTransfer.setData('nom-dechet', dechet.nom);
    });
}

/**
 * Initialise les événements sur les 3 poubelles
 */
function initialiserPoubelles() {
    let poubelles = document.querySelectorAll('.poubelle');

    poubelles.forEach(function(poubelle) {
        ajouterEvenementDragOverSurPoubelle(poubelle);
        ajouterEvenementDropSurPoubelle(poubelle);
        ajouterEvenementClicSurPoubelle(poubelle);
    });
}

/**
 * Autorise le drop sur une poubelle (dragover)
 */
function ajouterEvenementDragOverSurPoubelle(poubelle) {
    poubelle.addEventListener('dragover', function(event) {
        event.preventDefault();
    });
}

/**
 * Gère le drop d'une carte sur une poubelle
 */
function ajouterEvenementDropSurPoubelle(poubelle) {
    poubelle.addEventListener('drop', function(event) {
        event.preventDefault();

        console.log('📦 Carte déposée sur la poubelle !');

        // Récupérer les infos du dataTransfer
        let bonnePoubell = event.dataTransfer.getData('poubelle-correcte');
        let nomDechet = event.dataTransfer.getData('nom-dechet');
        let poubelleChoisie = this.dataset.bin;

        console.log('🔍 Déchet :', nomDechet);
        console.log('✅ Bonne réponse :', bonnePoubell);
        console.log('👉 Vous avez choisi :', poubelleChoisie);

        // Vérifier et remplacer la carte
        verifierEtRemplacer(bonnePoubell, poubelleChoisie, nomDechet);
    });
}

// 6. MODE CLIC-CLIC (MOBILE/TACTILE)
// ============================================

/**
 * Ajoute l'événement de clic sur une carte (sélection)
 */
function ajouterEvenementClicSurCarte(carte, dechet) {
    carte.addEventListener('click', function() {
        console.log('👆 Carte cliquée :', dechet.nom);

        // Désélectionner toutes les autres cartes
        deselectionnerToutesLesCartes();

        // Sélectionner cette carte
        this.classList.add('selectionnee');
        carteSelectionnee = this;

        console.log('✅ Carte sélectionnée :', dechet.nom);
    });
}

/**
 * Désélectionne toutes les cartes (retire la bordure verte)
 */
function deselectionnerToutesLesCartes() {
    let toutesLesCartes = document.querySelectorAll('.carte-dechet');
    toutesLesCartes.forEach(function(c) {
        c.classList.remove('selectionnee');
    });
}

/**
 * Ajoute l'événement de clic sur une poubelle (validation)
 */
function ajouterEvenementClicSurPoubelle(poubelle) {
    poubelle.addEventListener('click', function() {
        console.log('🗑️ Poubelle cliquée !');

        // Vérifier si une carte est sélectionnée
        if (carteSelectionnee === null) {
            console.log('⚠️ Aucune carte sélectionnée !');
            return;
        }

        console.log('✅ Une carte est sélectionnée, on vérifie...');

        // Récupérer les infos de la carte sélectionnée
        let bonnePoubell = carteSelectionnee.dataset.poubelle;
        let nomDechet = carteSelectionnee.querySelector('p').textContent;
        let poubelleChoisie = this.dataset.bin;

        console.log('🔍 Déchet :', nomDechet);
        console.log('✅ Bonne réponse :', bonnePoubell);
        console.log('👉 Vous avez choisi :', poubelleChoisie);

        // Vérifier et remplacer la carte
        verifierEtRemplacer(bonnePoubell, poubelleChoisie, nomDechet);

        // Réinitialiser la sélection
        carteSelectionnee.classList.remove('selectionnee');
        carteSelectionnee = null;

        console.log('🔄 Sélection réinitialisée');
    });
}

// 7. LOGIQUE DE VÉRIFICATION (COMMUNE)
// ============================================

/**
 * Vérifie si la réponse est correcte et remplace la carte
 * Cette fonction est utilisée par DRAG ET CLIC
 */
function verifierEtRemplacer(bonnePoubell, poubelleChoisie, nomDechet) {
    if (bonnePoubell === poubelleChoisie) {
        afficherSucces(nomDechet);
    } else {
        afficherErreur(bonnePoubell, nomDechet);
    }

    // Dans tous les cas, remplacer la carte
    remplacerCarte(nomDechet);
}

/**
 * Affiche un feedback de succès
 */
function afficherSucces(nomDechet) {
    console.log('🎉 BRAVO ! C\'est correct pour :', nomDechet);

    // Incrémenter le score
    scoreSession++;
    nombreCorrects++;
    nombreTentatives++;

    // Affichage du nouveau score
    mettreAJourAffichageScore();

    // TODO : Ajouter message de Récy positif

}

/**
 * Affiche un feedback d'erreur
 */
function afficherErreur(bonnePoubell, nomDechet) {
    console.log('❌ OUPS ! Ce n\'est pas la bonne poubelle :', nomDechet);
    console.log('💡 Il fallait la mettre dans la', bonnePoubell);

    // Comptage des tentatives (même fausses)
    nombreTentatives++;

    // TODO : Ajouter message de Récy correctif
}

function mettreAJourAffichageScore() {
    // Calculer le score total à afficher
    let scoreAffiche = scoreTotalUtilisateur + scoreSession;

    // Trouver l'élèment HTML où afficher le score
    let scoreDisplay = document.getElementById('score-display');

    // Vérifier que l'élèment existe
    if (scoreDisplay) {
        scoreDisplay.textContent = scoreAffiche + 'pts';
        console.log('Score mis à jour :', scoreAffiche, 'pts');
    } else {
        console.error('Element score-display introuvable');
    }
}

async function chargerInfosUtilisateur() {
    try {
        const response = await fetchWithAuth('/api/me', {
            method: 'GET'
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (data.success && data.data) {
            // afficher username
            const username = data.data.username;
            let userInfo = document.getElementById('user-info');
            if (userInfo) {
                userInfo.textContent = '👤 ' + username;
            }

            // récupère le score
            scoreTotalUtilisateur = data.data.total_score || 0;
            mettreAJourAffichageScore();
        }
    } catch (error) {
        scoreTotalUtilisateur = 0;
        mettreAJourAffichageScore();
    }
}

/**
 * Sauvegarde le score de la session en cours SANS quitter le jeu
 */
function sauvegarderScore() {
    console.log('💾 Sauvegarde du score en cours...');

    // Si aucun point, pas besoin de sauvegarder
    if (scoreSession === 0) {
        console.log('ℹ️ Aucun point à sauvegarder pour le moment');
        afficherMessageUtilisateur('Aucun point à sauvegarder pour le moment', 'info');
        return;
    }

    console.log('📊 Score session à sauvegarder :', scoreSession);
    console.log('⏰ tempsDebut:', tempsDebut);
    console.log('⏰ Date.now():', Date.now());

    // Préparation des données à envoyer
    let dureeMsPartie = Date.now() - tempsDebut;
    let donneesScore = {
        points: scoreSession,
        correct_items: nombreCorrects,
        total_items: nombreTentatives,
        duration_ms: dureeMsPartie
    };

    console.log('📤 Envoi des données :', donneesScore);

    // Désactiver le bouton pendant la sauvegarde (éviter double-clic)
    let btnSave = document.getElementById('btn-save');
    if (btnSave) {
        btnSave.disabled = true;
        btnSave.textContent = '⏳ Sauvegarde...';
    }

    // Envoyer à l'API
    fetchWithAuth('/api/scores', {
        method: 'POST',
        body: JSON.stringify(donneesScore)
    })
    .then(response => response.json())
    .then(data => {
        console.log('📥 Réponse de l\'API :', data);

        if (data.success === true) {
            console.log('🎉 Score sauvegardé avec succès !');
            console.log('🏆 Nouveau score total :', data.data.total_score);

            // MAJ du score total utilisateur
            scoreTotalUtilisateur = data.data.total_score;
            mettreAJourAffichageScore();

            // Réinitialiser le score de session (car déjà sauvegardé)
            scoreSession = 0;
            nombreCorrects = 0;
            nombreTentatives = 0;
            tempsDebut = Date.now(); // Nouveau départ pour la prochaine session

            // Afficher un message de succès
            afficherMessageUtilisateur('✅ Score sauvegardé avec succès !', 'success');

            // Réactiver le bouton
            if (btnSave) {
                btnSave.disabled = false;
                btnSave.textContent = '💾 Sauvegarder';
            }

        } else {
            console.error('❌ Erreur lors de la sauvegarde :', data);
            afficherMessageUtilisateur('❌ Erreur lors de la sauvegarde', 'error');

            // Réactiver le bouton
            if (btnSave) {
                btnSave.disabled = false;
                btnSave.textContent = '💾 Sauvegarder';
            }
        }
    })
    .catch(error => {
        console.error('❌ Erreur réseau :', error);
        afficherMessageUtilisateur('❌ Erreur de connexion. Score non sauvegardé.', 'error');

        // Réactiver le bouton
        if (btnSave) {
            btnSave.disabled = false;
            btnSave.textContent = '💾 Sauvegarder';
        }
    });
}

/**
 * Affiche un message temporaire à l'utilisateur
 */
function afficherMessageUtilisateur(message, type) {
    // Créer un élément pour le message
    let messageDiv = document.createElement('div');
    messageDiv.className = 'message-notification message-' + type;
    messageDiv.textContent = message;

    // Style par défaut (tu peux adapter dans ton CSS)
    messageDiv.style.position = 'fixed';
    messageDiv.style.top = '20px';
    messageDiv.style.left = '50%';
    messageDiv.style.transform = 'translateX(-50%)';
    messageDiv.style.padding = '15px 30px';
    messageDiv.style.borderRadius = '8px';
    messageDiv.style.fontWeight = 'bold';
    messageDiv.style.zIndex = '9999';
    messageDiv.style.animation = 'fadeIn 0.3s ease-in';

    // Couleurs selon le type
    if (type === 'success') {
        messageDiv.style.backgroundColor = '#4CAF50';
        messageDiv.style.color = 'white';
    } else if (type === 'error') {
        messageDiv.style.backgroundColor = '#f44336';
        messageDiv.style.color = 'white';
    } else {
        messageDiv.style.backgroundColor = '#2196F3';
        messageDiv.style.color = 'white';
    }

    // Ajouter au body
    document.body.appendChild(messageDiv);

    // Retirer après 3 secondes
    setTimeout(() => {
        messageDiv.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 3000);
}

// 8. REMPLACEMENT DES CARTES
// ============================================

/**
 * Remplace une carte triée par une nouvelle carte aléatoire
 */
function remplacerCarte(nomDechetATrier) {
    console.log('🔄 Remplacement de la carte :', nomDechetATrier);

    // 1. Trouver la carte dans le DOM
    let cartes = document.querySelectorAll('.carte-dechet');
    let carteATirer = null;

    cartes.forEach(function(carte) {
        let nomCarte = carte.querySelector('p').textContent;
        if (nomCarte === nomDechetATrier) {
            carteATirer = carte;
        }
    });

    // 2. Supprimer la carte du DOM
    if (carteATirer) {
        carteATirer.remove();
        console.log('❌ Carte retirée');
    }

    // 3. Choisir un nouveau déchet au hasard
    let dechetsMelanges = melangerTableau(tousLesDechets);
    let nouveauDechet = dechetsMelanges[0];

    console.log('➕ Nouveau déchet :', nouveauDechet.nom);

    // 4. Créer la nouvelle carte
    let zoneCartes = document.getElementById('cartes-zone');
    let nouvelleCarte = creerCarte(nouveauDechet);

    // 5. Ajouter la nouvelle carte
    zoneCartes.appendChild(nouvelleCarte);

    console.log('✅ Nouvelle carte ajoutée !');
}
