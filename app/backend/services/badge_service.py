from datetime import datetime
from sqlalchemy import func
from db.models import Badge, Score, User, UserBadge

class BadgeService:
    def __init__(self, db):
        self.db = db
        self.badges = []

    def get_user_badges(self, user_id):

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
        # Récupération utilisateur et ses badges existants
        utilisateur = self.db.session.get(User, user_id)
        if not utilisateur:
            return []

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
                    self.db.add(new_entry)

                    #Ajout de la liste des nouveaux badges
                    new_badges.append({
                        "code": badge.code,
                        "label": badge.label,
                        "description": badge.description,
                        "awarded_at": str(maintenant)
                    })
        self.db.commit()
        return {
            "success": True,
            "data": new_badges,
            "status_code": 200
        }

    def get_all_badges(self):
        if not self.badges: # si la liste est vide
            self.load_badges()

        badge_list = []
        for badge in self.badges:
            badge_list.append({
                "code": badge.code,
                "label": badge.label,
                "description": badge.description
            })

        return badge_list

    def load_badges(self):
        self.badges = self.db.session.query(Badge).all()
