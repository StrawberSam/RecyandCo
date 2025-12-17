"""
Service de gestion des scores pour Récy&Co.

Ce module gère toute la logique liée aux scores des parties :
ajout de nouveaux scores, mise à jour du score total, récupération
de l'historique et du classement global.

Classes:
    ScoreService: Service principal pour la gestion des scores et statistiques
"""

from sqlalchemy import desc
from db.models import Score, User
from utils.services_utils import validate_and_get_user, validate_limit


class ScoreService:
    """
    Service gérant les scores des parties et les statistiques des utilisateurs.

    Ce service encapsule toute la logique liée aux scores :
    - Ajout d'un score après une partie
    - Mise à jour du score total de l'utilisateur
    - Récupération de l'historique des scores d'un utilisateur
    - Génération du classement global (leaderboard)
    - Calcul des statistiques de jeu d'un utilisateur

    Le système de points est simple : 1 item correctement trié = 1 point.
    Les points sont cumulés dans le champ total_score de l'utilisateur,
    qui sert ensuite de monnaie virtuelle dans la boutique.

    Attributes:
        db: Instance de SQLAlchemy pour les opérations de base de données
    """

    def __init__(self, db):
        """
        Initialise le service de gestion des scores.

        Args:
            db: Instance SQLAlchemy pour les accès à la base de données
        """
        self.db = db

    def add_score(self, user_id, points, correct_items=None, total_items=None, duration_ms=None):
        """
        Ajoute un nouveau score après une partie et met à jour le score total.

        Cette méthode est appelée à la fin de chaque partie pour enregistrer
        les performances du joueur. Elle effectue plusieurs actions :
        1. Valide les données d'entrée
        2. Crée un nouvel enregistrement Score dans la base de données
        3. Met à jour le score total de l'utilisateur (total_score += points)
        4. Commit les changements en base de données

        Args:
            user_id (int): Identifiant de l'utilisateur
            points (int): Nombre de points gagnés (1 point = 1 item trié correctement)
            correct_items (int, optional): Nombre d'items correctement triés (par défaut 0)
            total_items (int, optional): Nombre total d'items présentés (par défaut 0)
            duration_ms (int, optional): Durée de la partie en millisecondes (par défaut 0)

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'ajout a réussi
                - data (dict): Informations sur le score ajouté :
                    - user_id (int): Identifiant de l'utilisateur
                    - total_score (int): Nouveau score total après mise à jour
                    - score_id (int): Identifiant du score créé
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Score ajouté avec succès
                    - 400 : Données invalides (user_id pas entier ou points négatifs)
                    - 404 : Utilisateur introuvable

        Note:
            Le champ `points` devrait normalement être égal à `correct_items`
            dans votre logique métier (1 point = 1 item correct).
        """

        # Vérifications
        utilisateur, error = validate_and_get_user(self.db, user_id)
        if error:
            return error

        assert utilisateur is not None

        if points < 0:
            return {"success": False, "message": "Les données de la partie sont invalides", "status_code": 400}

        new_score = Score(
            user_id=user_id,
            points=points,
            correct_items=correct_items or 0,
            total_items=total_items or 0,
            duration_ms=duration_ms or 0
        )

        # Ajout à la session
        self.db.session.add(new_score)

        # MAJ du total
        utilisateur.total_score += points

        # Commit + retourner la réponse
        self.db.session.commit()

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_score": utilisateur.total_score,
                "score_id": new_score.id
            },
            "status_code": 200
        }

    def get_user_scores(self, user_id):
        """
        Récupère les informations de score d'un utilisateur.

        Cette méthode retourne actuellement le score total de l'utilisateur.
        Elle pourrait être étendue pour retourner l'historique complet
        des parties.

        Args:
            user_id (int): Identifiant de l'utilisateur

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'opération a réussi
                - data (dict): Informations de score :
                    - user_id (int): Identifiant de l'utilisateur
                    - total_score (int): Score total accumulé
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Données récupérées avec succès
                    - 400 : user_id invalide (pas un entier)
                    - 404 : Utilisateur introuvable

        Note:
            Cette méthode pourrait être améliorée pour retourner la liste
            complète des parties jouées (historique des scores).
        """
        utilisateur, error = validate_and_get_user(self.db, user_id)
        if error:
            return error

        assert utilisateur is not None

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_score": utilisateur.total_score
            },
            "status_code": 200
        }

    def get_leaderboard(self, limit=15):
        """
        Récupère le classement global des utilisateurs par score total.

        Cette méthode génère un classement (leaderboard) des meilleurs
        joueurs, triés par score total décroissant. C'est utile pour
        créer une dynamique compétitive et encourager les utilisateurs.

        Args:
            limit (int, optional): Nombre d'utilisateurs à retourner (par défaut 15)

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'opération a réussi
                - data (list): Liste de dictionnaires triés par score, chacun contenant :
                    - username (str): Nom d'utilisateur
                    - total_score (int): Score total accumulé
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Classement récupéré avec succès
                    - 400 : limit invalide (pas un entier)

        Note:
            Le classement est basé sur le score total (total_score),
            pas sur le score d'une seule partie.
        """
        # Validation du paramètre limit
        error = validate_limit(limit)
        if error:
            return error

        resultat = (
            self.db.session.query(User)
            .with_entities(User.username, User.total_score)
            .order_by(desc(User.total_score))
            .limit(limit)
            .all()
        )

        leaderboard = []
        for username, total_score in resultat:
            leaderboard.append({
                "username": username,
                "total_score": total_score
            })

        return {
            "success": True,
            "data": leaderboard,
            "status_code": 200
        }

    def get_user_stats(self, user_id: int):
        """
        Récupère les statistiques détaillées de jeu d'un utilisateur.

        Cette méthode calcule plusieurs statistiques utiles pour afficher
        un profil utilisateur ou un tableau de bord personnel :
        - Nombre total de parties jouées
        - Meilleur score obtenu dans une seule partie
        - Nombre total d'items correctement triés (tous temps)

        Args:
            user_id (int): Identifiant de l'utilisateur

        Returns:
            dict: Dictionnaire contenant :
                - parties_jouees (int): Nombre de parties jouées
                - points (int): Meilleur score d'une partie (0 si aucune partie)
                - correct_items (int): Total d'items correctement triés (0 si aucune partie)

        Note:
            Cette méthode ne valide pas l'existence de l'utilisateur.
            Si l'utilisateur n'existe pas ou n'a jamais joué, elle retourne
            des valeurs à 0.
        """

        # Validation et récupération utilisateur
        _, error = validate_and_get_user(self.db, user_id)
        if error:
            return error

        # 1. Compter le nombre de parties
        parties_jouees = Score.query.filter_by(user_id=user_id).count()

        # 2. Trouver le meilleur score (le plus grand 'points')
        meilleur_score = self.db.session.query(self.db.func.max(Score.points))\
            .filter_by(user_id=user_id)\
            .scalar()

        # 3. Additionner tous les 'correct_items'
        total_correct_items = self.db.session.query(self.db.func.sum(Score.correct_items))\
            .filter_by(user_id=user_id)\
            .scalar()

        # Si l'utilisateur n'a jamais joué, on met des valeurs par défaut à 0
        if meilleur_score is None:
            meilleur_score = 0
        if total_correct_items is None:
            total_correct_items = 0

        return {
            "success": True,
            "data": {
                "parties_jouees": parties_jouees,
                "points": meilleur_score,
                "correct_items": total_correct_items
            },
            "status_code": 200
        }
