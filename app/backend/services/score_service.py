from sqlalchemy import desc
from db.models import db, User

class ScoreService:
    """
    Service pour gérer les scores des utilisateurs.
    Rôles :
    - Ajouter un score après une partie.
    - Mettre à jour le total_score de l’utilisateur.
    - Récupérer l’historique des scores d’un utilisateur.
    - Récupérer le classement global (leaderboard).
    """

    def __init__(self, db):
        self.db = db

    def add_score(self, user_id, points):
        """
        Ajoute un nouveau score pour un utilisateur et met à jour son total_score.

        Args:
            user_id (int): identifiant de l’utilisateur
            points (int): points gagnés (1 point = 1 item trié correct)

        Returns:
            dict: infos du score ajouté + total_score mis à jour
        """

        # Vérifications
        if not isinstance(user_id, int):
            return {"success": False, "message": "user_id doit être un entier", "status_code": 400}

        utilisateur = User.query.get(user_id)
        if not utilisateur:
            return {"success": False, "message": "User non trouvé", "status_code": 404}

        if points < 0:
            return {"success": False, "message": "Les données de la partie sont invalides", "status_code": 400}

        # MAJ du total
        utilisateur.total_score += points

        # Commit + retourner la réponse
        db.session.commit()

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_score": utilisateur.total_score
            },
            "status_code": 200
        }

    def get_user_scores(self, user_id):
        """
        Récupère la liste des scores d’un utilisateur (historique).

        Args:
            user_id (int): identifiant de l’utilisateur

        Returns:
            list: liste de dicts contenant les scores
        """
        if not isinstance(user_id, int):
            return {"success": False, "message": "user_id doit être un entier", "status_code": 400}

        utilisateur = User.query.get(user_id)
        if not utilisateur:
            return {"success": False, "message": "User non trouvé", "status_code": 404}

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_score": utilisateur.total_score
            },
            "status_code": 200
        }

    def get_leaderboard(self, limit = 15):
        """
        Récupère le classement global des utilisateurs par total_score.

        Args:
            limit (int): nombre d’utilisateurs à renvoyer (par défaut 10)

        Returns:
            list: classement sous forme de dicts {username, total_score}
        """
        if not isinstance(limit, int):
            return {"success": False, "message": "Limit doit être un entier", "status_code": 400}

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
