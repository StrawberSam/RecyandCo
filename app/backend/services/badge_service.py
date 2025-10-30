"""
Service de gestion des badges pour Récy&Co.

Ce module gère toute la logique de gamification liée aux badges :
attribution automatique selon les performances, récupération des badges
d'un utilisateur, et chargement des badges disponibles.

Classes:
    BadgeService: Service principal pour la gestion des badges et récompenses

Author: Roche Samira
Project: Récy&Co - Sorting is fun!
"""

from datetime import datetime
from sqlalchemy import func
from db.models import Badge, User, UserBadge

class BadgeService:
    """
    Service gérant l'attribution et la récupération des badges.

    Ce service encapsule toute la logique de gamification liée aux badges :
    - Récupération des badges débloqués par un utilisateur
    - Attribution automatique de nouveaux badges selon les performances
    - Chargement de la liste des badges disponibles

    Les badges sont attribués selon différents critères :
    - Score total accumulé (badges de progression)
    - Performance dans une partie (badges de rapidité, perfection)
    - Nombre de parties jouées (badges d'assiduité)
    - Collection de badges (méta-badges)

    Attributes:
        db: Instance de SQLAlchemy pour les opérations de base de données
        badges (list): Liste des badges disponibles (chargée depuis la DB)
    """

    def __init__(self, db):
        """
        Initialise le service de gestion des badges.

        Args:
            db: Instance SQLAlchemy pour les accès à la base de données
        """
        self.db = db
        self.badges = []

    def get_user_badges(self, user_id):
        """
        Récupère tous les badges débloqués par un utilisateur.

        Cette méthode effectue une jointure entre UserBadge et Badge
        pour obtenir les informations complètes de chaque badge débloqué.

        Args:
            user_id (int): Identifiant de l'utilisateur

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'opération a réussi
                - data (list): Liste de dictionnaires, chacun contenant :
                    - code (str): Code unique du badge
                    - label (str): Nom du badge
                    - description (str): Description du badge
                    - awarded_at (str): Date et heure de déblocage
                  OU
                - message (str): Message d'erreur si échec
                - status_code (int): Code HTTP approprié
                    - 200 : Badges récupérés avec succès
                    - 400 : user_id invalide (pas un entier)
                    - 404 : Utilisateur introuvable
        """

        if not isinstance(user_id, int):
            return {"success": False, "message": "user_id doit être un entier", "status_code": 400}

        utilisateur = self.db.session.get(User, user_id)
        if not utilisateur:
            return {"success": False, "message": "User non trouvé", "status_code": 404}

        # Récupère les badge de l'user
        resultat = (
            self.db.session.query(UserBadge)
            .filter(UserBadge.user_id == user_id)
            .join(Badge)
            .with_entities(Badge.code, Badge.label, Badge.description, UserBadge.awarded_at)
            .all()
        )

        badges_list = []
        for code, label, description, awarded_at in resultat:
            badges_list.append({
                "code": code,
                "label": label,
                "description": description,
                "awarded_at": str(awarded_at)
                })

        return {
            "success": True,
            "data": badges_list,
            "status_code": 200
        }

    def check_and_award_badges(self, user_id, score):
        """
        Vérifie et attribue automatiquement les nouveaux badges gagnés.

        Cette méthode est appelée après chaque partie pour vérifier si
        l'utilisateur a débloqué de nouveaux badges. Elle évalue tous les
        critères de déblocage et attribue uniquement les badges pas encore
        possédés.

        Les critères de déblocage incluent :
        - Score total accumulé (TRIEUR_MALIN, TRIEUR_NOVICE, etc.)
        - Performance de la partie actuelle (PERFECT_RUN, TRIEUR_RAPIDE)
        - Nombre d'items triés (TRIEUR_JOUEUR)
        - Collection de badges existants (PETIT_COLLECTIONNEUR)

        Args:
            user_id (int): Identifiant de l'utilisateur
            score (Score): Objet Score de la partie qui vient d'être jouée

        Returns:
            dict: Dictionnaire contenant :
                - success (bool): True si l'opération a réussi
                - data (list): Liste des nouveaux badges débloqués, chacun contenant :
                    - code (str): Code unique du badge
                    - label (str): Nom du badge
                    - description (str): Description du badge
                    - awarded_at (str): Date et heure de déblocage
                - status_code (int): 200 (succès)

        Returns:
            list: Liste vide si l'utilisateur n'existe pas ou aucun nouveau badge
        """

        # Récupération utilisateur et ses badges existants
        utilisateur = self.db.session.get(User, user_id)
        if not utilisateur:
            return {"success": False, "message": "Utilisateur introuvable", "status_code": 404}

        user_badges_response = self.get_user_badges(user_id)
        user_badges = user_badges = user_badges_response["data"]
        owned_badges = {badge["code"] for badge in user_badges}

        # Points totaux = compteur global stocké directement
        user_total_points = utilisateur.total_score
        # Définition des règles des badges
        badge_rules = {
            # Badges enfants
            "TRIEUR_MALIN": lambda: user_total_points >= 10,
            "TRIEUR_FUTE": lambda: user_total_points >= 40,
            "TRIEUR_PROPRET": lambda: user_total_points >= 60,
            "TRIEUR_CHAMPION": lambda: user_total_points >=80,
            "TRIEUR_RAPIDE": lambda: score.duration_ms and score.duration_ms < 2000, # 2 secondes
            "TRIEUR_JOUEUR": lambda: score.total_items >= 20,
            "AMI_DE_RECY": lambda: user_total_points >= 25,
            # Badge progression "sérieux"
            "FIRST_GAME": lambda: score.correct_items >= 1,
            "PERFECT_RUN": lambda: score.correct_items == score.total_items,
            "TRIEUR_NOVICE": lambda: user_total_points >= 30,
            "TRIEUR_DEBUTANT": lambda: user_total_points >= 50,
            "TRIEUR": lambda: user_total_points >= 70,
            "TRIEUR_APPLIQUE": lambda: user_total_points >= 100,
            "200_POINTS": lambda: user_total_points >= 200,
            "TRIEUR_ASSIDU": lambda: user_total_points >= 300,
            "400_POINTS": lambda: user_total_points >= 400,
            "TRIEUR_CONFIRME": lambda: user_total_points >= 500,
            # Badge collectionneur
            "PETIT_COLLECTIONNEUR": lambda: len(owned_badges) >= 5
        }

        # Comparaison avec self.badges pour voir lesquels attribuer
        new_badges = []
        maintenant = datetime.now()

        for badge in self.badges:
            if badge.code in badge_rules and badge.code not in owned_badges:
                if badge_rules[badge.code]():

                    # création dans db
                    new_entry = UserBadge(user_id=user_id, badge_id=badge.id, awarded_at=maintenant)
                    self.db.session.add(new_entry)

                    #Ajout de la liste des nouveaux badges
                    new_badges.append({
                        "code": badge.code,
                        "label": badge.label,
                        "description": badge.description,
                        "awarded_at": str(maintenant)
                    })
        self.db.session.commit()
        return {
            "success": True,
            "data": new_badges,
            "status_code": 200
        }

    def get_all_badges(self):
        """
        Récupère la liste de tous les badges disponibles dans l'application.

        Cette méthode charge tous les badges depuis la base de données
        si ce n'est pas déjà fait, puis retourne leur liste.

        Returns:
            list: Liste de dictionnaires, chacun contenant :
                - code (str): Code unique du badge
                - label (str): Nom du badge
                - description (str): Description et condition de déblocage

        Note:
            Cette méthode ne retourne pas les dates de déblocage car elle
            liste les badges disponibles, pas les badges d'un utilisateur.
        """
        if not self.badges: # si la liste est vide
            self.load_badges()

        badge_list = []
        for badge in self.badges:
            badge_list.append({
                "code": badge.code,
                "label": badge.label,
                "description": badge.description
            })

        return {
            "success": True,
            "data": badge_list,
            "status_code": 200
        }

    def load_badges(self):
        """
        Charge tous les badges depuis la base de données.

        Cette méthode est appelée automatiquement par get_all_badges()
        la première fois, pour éviter de recharger les badges à chaque
        appel. Les badges sont stockés dans self.badges pour réutilisation.

        Note:
            Cette méthode est utilisée en interne par la classe.
            Les utilisateurs externes devraient utiliser get_all_badges().
        """
        self.badges = self.db.session.query(Badge).all()
